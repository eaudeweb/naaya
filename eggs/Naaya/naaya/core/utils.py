from datetime import datetime
import re
import sys
import htmlentitydefs
import warnings
import tempfile
import urllib
import socket
import scrubber

if 'any' not in dir(__builtins__):
    from Products.NaayaCore.backport import any
    scrubber.any = any
sanitize = scrubber.Scrubber().scrub


content_type_to_icons = {
    "audio/aiff": ["AIFF", "aiff"],
    "application/octet-stream": ["BINARY", "file"],
    "image/bmp": ["BMP", "bmp"],
    "text/css": ["CSS", "css"],
    "application/msword": ["DOC", "doc"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        ["DOCX", "docx"],
    "image/gif": ["GIF", "gif"],
    "application/x-gzip": ["GZ", "gz"],
    "text/html": ["HTML", "html"],
    "image/pjpeg": ["JPEG", "jpeg"],
    "image/jpeg": ["JPEG", "jpeg"],
    "image/jpg": ["JPG", "jpg"],
    "application/x-javascript": ["JS", "js"],
    "application/msaccess": ["MDB", "mdb"],
    "audio/mpeg": ["MP3", "mp3"],
    "video/mpeg": ["MPG", "mpg"],
    "video/mp4": ["MP4", "mp4"],
    "text/x-ms-odc": ["ODC", "odc"],
    "application/vnd.oasis.opendocument.formula": ["ODF", "odf"],
    "application/vnd.oasis.opendocument.graphics": ["ODG", "odg"],
    "application/vnd.oasis.opendocument.presentation": ["ODP", "odp"],
    "application/vnd.oasis.opendocument.spreadsheet": ["ODS", "ods"],
    "application/vnd.oasis.opendocument.text": ["ODT", "odt"],
    "application/pdf": ["PDF", "pdf"],
    "image/png": ["PNG", "png"],
    "image/x-png": ["PNG", "png"],
    "application/vnd.ms-powerpoint": ["PPT", "ppt"],
    "application/"
    "vnd.openxmlformats-officedocument.presentationml.presentation":
        ["PPTX", "pptx"],
    "application/postscript": ["PS", "ps"],
    "application/x-shockwave-flash": ["SWF", "swf"],
    "application/vnd.sun.xml.calc": ["SXC", "sxc"],
    "application/vnd.sun.xml.draw": ["SXD", "sxd"],
    "application/vnd.sun.xml.impress": ["SXI", "sxi"],
    "application/vnd.sun.xml.writer": ["SXW", "sxw"],
    "application/x-tar": ["TAR", "tar"],
    "application/x-compressed": ["TGZ", "tgz"],
    "text/plain": ["TXT", "txt"],
    "text/x-vcard": ["VCF", "vcf"],
    "audio/wav": ["WAV", "wav"],
    "audio/x-ms-wma": ["WMA", "wma"],
    "video/x-ms-wmv": ["WMV", "wmv"],
    "application/vnd.ms-excel": ["XLS", "xls"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        ["XLSX", "xlsx"],
    "text/xml": ["XML", "xml"],
    "application/x-xpinstall": ["XPI", "xpi"],
    "application/x-zip-compressed": ["ZIP", "zip"],
    "application/zip": ["ZIP", "zip"],
}


def icon_for_content_type(content_type, approved=True):
    title, image_id = content_type_to_icons.get(content_type, ["BINARY",
                                                               "file"])
    if approved:
        image_filename = image_id+'.png'
    else:
        title = 'This %s file is not approved' % title
        image_filename = image_id+'_marked.png'
    return {'title': title,
            'url': '++resource++naaya.mime_icons/'+image_filename}


def get_noaq_attr(obj, attr, default):
    """
    Return the wanted attribute without
    checking the acquisition tree or `default`.
    """
    return getattr(obj.aq_base, attr, default)


def call_method(obj, attr, default):
    """
    Return the result of calling `obj`s `attr`
    or `default` if `obj` doesn't have `attr`.
    """
    if get_noaq_attr(obj, attr, default) != default:
        return getattr(obj, attr)()
    else:
        return default


def force_to_unicode(s):
    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        try:
            return s.decode('utf-8')
        except UnicodeDecodeError:
            return s.decode('latin-1')
    else:
        raise ValueError('expected `str` or `unicode`')

_cooldown_map = {}


def cooldown(name, interval):
    """
    Return ``True`` if called sooner than ``interval`` with the same
    ``name`` argument. Intended usage::

        @component.adapter(INySite, IHeartbeat)
        def hourly_foobar(site, hb):
            if cooldown('foobar %r' % ofs_path(site), timedelta(hours=1)):
                return
            # ... code that will run (almost) every hour

        component.provideHandler(hourly_foobar)
    """
    now = datetime.now()
    if name in _cooldown_map and _cooldown_map[name] + interval > now:
        return True
    else:
        _cooldown_map[name] = now
        return False


def unescape_html_entities(text):
    # from http://effbot.org/zone/re-sub.htm#unescape-html
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def is_ajax(request):
    """Check if an REQUEST object has 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'

    """
    return request.environ.get('HTTP_X_REQUESTED_WITH', '') == 'XMLHttpRequest'


def render_macro(context, template_name, macro, **kw):
    """ Render just a part of the macro """
    from Products.PageTemplates.PageTemplate import PageTemplate
    template = PageTemplate()
    template.write("<metal:block\
        use-macro=\"python: here.getFormsTool().getForm('%s').macros['%s']\"\
        />" % (template_name, macro))
    kw.update({'here': context, 'context': context})
    return template.pt_render(extra_context=kw)


def pretty_size(n_bytes):
    if n_bytes < 1024:
        return '%d bytes' % n_bytes
    elif n_bytes < 1024**2:
        return '%d KB' % (n_bytes/1024)
    elif n_bytes < 1024**3:
        return '%d MB' % (n_bytes/1024**2)
    else:
        return '%d GB' % (n_bytes/1024**3)

VALID_EMAIL_PATTERN = re.compile("(?:^|\s)[-a-z0-9_.]+@"
                                 "(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",
                                 re.IGNORECASE)


def is_valid_email(email):
    """
    Validate e-mail address against regular expression
    """
    if VALID_EMAIL_PATTERN.match(str(email)):
        return True
    return False


# these functions were initially defined here, but they are zope2-specific,
# and belong to zope2util, so we moved them over there.

def relative_object_path(obj, ancestor):
    warnings.warn("naaya.core.utils.relative_object_path moved "
                  "to naaya.core.zope2util",
                  DeprecationWarning, stacklevel=2)
    import zope2util
    return zope2util.relative_object_path(obj, ancestor)


def path_in_site(obj):
    warnings.warn("naaya.core.utils.path_in_site moved "
                  "to naaya.core.zope2util",
                  DeprecationWarning, stacklevel=2)
    import zope2util
    return zope2util.path_in_site(obj)


def ofs_path(obj):
    warnings.warn("naaya.core.utils.ofs_path moved "
                  "to naaya.core.zope2util",
                  DeprecationWarning, stacklevel=2)
    import zope2util
    return zope2util.ofs_path(obj)


def download_to_temp_file(url):
    """
    Download contents of URL to a temporary file created with
    `tempfile.TemporaryFile`. Returns an open file containing the response
    body.  When the file is closed it will be automatically removed.
    """
    temp_file = tempfile.TemporaryFile()
    url_file = urllib.urlopen(url)
    try:
        while True:
            buf = url_file.read(2**16)
            if not buf:
                break
            temp_file.write(buf)
    finally:
        url_file.close()
    temp_file.seek(0)
    return temp_file


def set_default_socket_timeout_to_1min():
    """
    Sets the default timeout for new socket objects to 1 minute.

    Default in python is no timeout (None). This is unacceptable e.g. for cron
    jobs that can keep threads blocked indefinitely waiting to open an URL.
    This should be called when starting zope.
    """
    socket.setdefaulttimeout(60)  # in seconds

_illegal_unichrs = [
    (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
    (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
    (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
    (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
    (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
    (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
    (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
    (0x10FFFE, 0x10FFFF),
]

_illegal_ranges = ["%s-%s" % (unichr(low), unichr(high))
                   for (low, high) in _illegal_unichrs
                   if low < sys.maxunicode]

_illegal_xml_re = re.compile(u'[%s]' % u''.join(_illegal_ranges))


def replace_illegal_xml(text, replacement=''):
    return _illegal_xml_re.sub(replacement, text)


def trim(message):
    """ Remove leading and trailing empty paragraphs """
    message = re.sub(r'^\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*', '', message)
    message = re.sub(r'\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*$', '', message)
    return message


def cleanup_message(message):
    return sanitize(trim(message)).strip()


def str2bool(string):
    return string in [True, 'true', 'True']


def file_length(file_name):
    file_content = open(file_name, 'r+')
    length = len(file_content.readlines())
    file_content.close()

    return length


def get_or_create_attribute(ob, attr, default_value):
    if not hasattr(ob, attr):
        setattr(ob, attr, default_value)
    return ob
