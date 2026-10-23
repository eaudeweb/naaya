"""Plain text from uploaded files, for the full-text catalog index."""

import logging
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from html.parser import HTMLParser
from xml.etree import ElementTree

log = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024
MAX_TEXT_LENGTH = 1024 * 1024
COMMAND_TIMEOUT = 60

PDF_COMMAND = ['pdftotext', '-q', '-enc', 'UTF-8', '{path}', '-']
# legacy Office formats via catdoc, used only when installed; -s is the 8-bit codepage
LEGACY_COMMANDS = {
    '.doc': ['catdoc', '-s', 'cp1252', '-d', 'utf-8', '{path}'],
    '.xls': ['xls2csv', '-s', 'cp1252', '-d', 'utf-8', '{path}'],
    '.ppt': ['catppt', '-s', 'cp1252', '-d', 'utf-8', '{path}'],
}
_missing_binaries = set()

OOXML_PARTS = {
    'word/': re.compile(r'word/(document|header\d*|footer\d*|footnotes|'
                        r'endnotes)\.xml$'),
    'xl/': re.compile(r'xl/(sharedStrings|worksheets/sheet\d+)\.xml$'),
    'ppt/': re.compile(r'ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml$'),
}
# element local names that end a line of text
BREAK_TAGS = {'p', 'h', 'br', 'line-break', 'tc', 'si', 'row',
              'table-cell', 'list-item'}
SPACE_TAGS = {'s', 'tab'}
TEXT_TAGS = {'t'}


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _xml_text(data, ooxml):
    """Text of an OOXML part (only <t> elements) or an ODF part (all text)."""
    out = []

    def walk(el):
        name = _local(el.tag)
        if name in SPACE_TAGS:
            out.append(' ')
        if not ooxml or name in TEXT_TAGS:
            out.append(el.text or '')
        for child in el:
            walk(child)
        if name in BREAK_TAGS:
            out.append('\n')
        if not ooxml:
            out.append(el.tail or '')

    walk(ElementTree.fromstring(data))
    return ''.join(out)


def _zip_text(path):
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        odf = 'mimetype' in names and zf.read('mimetype').startswith(
            b'application/vnd.oasis.opendocument')
        if odf and 'content.xml' in names:
            return _xml_text(zf.read('content.xml'), ooxml=False)
        parts = []
        for prefix, pattern in OOXML_PARTS.items():
            for name in sorted(names):
                if name.startswith(prefix) and pattern.match(name):
                    parts.append(_xml_text(zf.read(name), ooxml=True))
        return '\n'.join(parts)


class _HTMLText(HTMLParser):

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1
        self.out.append(' ')

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_to_text(text):
    parser = _HTMLText()
    parser.feed(text)
    parser.close()
    return ''.join(parser.out)


RTF_SKIP_GROUPS = {'fonttbl', 'colortbl', 'stylesheet', 'info', 'pict',
                   'header', 'footer', 'listtable', 'listoverridetable',
                   'rsidtbl', 'generator', 'xmlnstbl', 'themedata',
                   'colorschememapping', 'latentstyles', 'datastore'}
RTF_TOKEN = re.compile(r"\\([a-z]+)(-?\d+)? ?|\\'([0-9a-f]{2})|\\(.)|([{}])|"
                       r"([^\\{}\r\n]+)", re.I)


def rtf_to_text(data):
    """Text of an RTF document; skips font, color, style and picture tables."""
    text = data.decode('latin-1')
    out, stack, skip, fallback = [], [], False, 0
    for word, arg, hexcode, char, brace, plain in RTF_TOKEN.findall(text):
        if brace == '{':
            stack.append(skip)
        elif brace == '}':
            skip = stack.pop() if stack else False
        elif char == '*':
            skip = True
        elif char:
            if not skip:
                out.append({'~': ' ', '\n': '\n'}.get(char, char))
        elif word:
            if word.lower() in RTF_SKIP_GROUPS:
                skip = True
            elif not skip and word in ('par', 'line', 'row', 'cell', 'tab'):
                out.append('\n' if word != 'tab' else ' ')
            elif not skip and word == 'u' and arg:
                out.append(chr(int(arg) % 65536))
                fallback = 1  # \u is followed by one ANSI fallback char
        elif hexcode:
            if fallback:
                fallback = 0
            elif not skip:
                out.append(bytes([int(hexcode, 16)]).decode('cp1252',
                                                            'replace'))
        elif plain and not skip:
            out.append(plain[fallback:])
            fallback = 0
    return ''.join(out)


def _run(command, path):
    if command[0] in _missing_binaries:
        return None
    if shutil.which(command[0]) is None:
        _missing_binaries.add(command[0])
        log.warning('%s is not installed, skipping full-text extraction '
                    'for these files', command[0])
        return None
    args = [path if arg == '{path}' else arg for arg in command]
    result = subprocess.run(args, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, timeout=COMMAND_TIMEOUT,
                            check=True)
    return result.stdout.decode('utf-8', 'replace')


def _kind(head, content_type, filename):
    content_type = (content_type or '').lower()
    ext = os.path.splitext(filename or '')[1].lower()
    if head.startswith(b'%PDF') or content_type == 'application/pdf':
        return 'pdf'
    if head.startswith(b'PK'):
        return 'zip'
    if head.startswith(b'{\\rtf'):
        return 'rtf'
    if ext in LEGACY_COMMANDS:
        return ext
    if 'html' in content_type or ext in ('.html', '.htm'):
        return 'html'
    if content_type.startswith('text/') or ext in ('.txt', '.csv'):
        return 'text'
    return None


def _decode(data):
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return data.decode('latin-1')


def _extract(path, content_type, filename):
    if os.path.getsize(path) > MAX_FILE_SIZE:
        return ''
    with open(path, 'rb') as f:
        head = f.read(8)
    kind = _kind(head, content_type, filename)
    if kind is None:
        return ''
    if kind == 'pdf':
        return _run(PDF_COMMAND, path)
    if kind in LEGACY_COMMANDS:
        return _run(LEGACY_COMMANDS[kind], path)
    if kind == 'zip':
        return _zip_text(path)
    with open(path, 'rb') as f:
        data = f.read()
    if kind == 'rtf':
        return rtf_to_text(data)
    if kind == 'html':
        return html_to_text(_decode(data))
    return _decode(data)


def extract_text(data=None, content_type='', filename='', path=None):
    """Searchable text of bytes, a file object or a file on disk; '' on error."""
    return try_extract_text(data, content_type, filename, path) or ''


def try_extract_text(data=None, content_type='', filename='', path=None):
    """Like extract_text, but None when the converter binary is missing."""
    tmp_path = None
    try:
        if path is None:
            if hasattr(data, 'read'):
                data = data.read()
            if isinstance(data, str):
                data = data.encode('utf-8')
            if not data or len(data) > MAX_FILE_SIZE:
                return ''
            fd, tmp_path = tempfile.mkstemp(prefix='naaya-text-')
            with os.fdopen(fd, 'wb') as f:
                f.write(data)
            path = tmp_path
        text = _extract(path, content_type, filename)
    except Exception as e:
        log.warning('Could not extract text from %r (%s): %s',
                    filename, content_type, e)
        return ''
    finally:
        if tmp_path is not None:
            os.unlink(tmp_path)
    if text is None:
        return None
    text = re.sub(r'[ \t\r\f\v]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n', text).strip()
    return text[:MAX_TEXT_LENGTH]
