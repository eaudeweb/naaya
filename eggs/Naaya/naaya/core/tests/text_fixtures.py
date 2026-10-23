"""Small documents with known text, built in memory for extraction tests."""

import zipfile
from io import BytesIO


def make_pdf(text):
    """A one-page PDF showing `text` (ASCII) in Helvetica."""
    stream = ('BT /F1 12 Tf 72 720 Td (%s) Tj ET' % text).encode('ascii')
    objects = [
        b'<< /Type /Catalog /Pages 2 0 R >>',
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
        b'/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>',
        b'<< /Length %d >>\nstream\n' % len(stream) + stream +
        b'\nendstream',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    ]
    out = BytesIO()
    out.write(b'%PDF-1.4\n')
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(b'%d 0 obj\n' % number + body + b'\nendobj\n')
    xref = out.tell()
    out.write(b'xref\n0 %d\n0000000000 65535 f \n' % (len(objects) + 1))
    for offset in offsets:
        out.write(b'%010d 00000 n \n' % offset)
    out.write(b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'
              % (len(objects) + 1, xref))
    return out.getvalue()


def _zip(files):
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as zf:
        for name, data in files:
            zf.writestr(name, data)
    return out.getvalue()


W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def make_docx(text):
    # the word is split over two runs, as Word often does
    half = len(text) // 2
    return _zip([
        ('[Content_Types].xml', '<Types/>'),
        ('word/document.xml',
         '<w:document xmlns:w="%s"><w:body><w:p><w:r><w:t>%s</w:t></w:r>'
         '<w:r><w:t>%s</w:t></w:r></w:p><w:p><w:r><w:t>second</w:t></w:r>'
         '</w:p></w:body></w:document>' % (W, text[:half], text[half:])),
    ])


def make_xlsx(text):
    return _zip([
        ('[Content_Types].xml', '<Types/>'),
        ('xl/sharedStrings.xml',
         '<sst xmlns="%s"><si><t>%s</t></si></sst>' % (S, text)),
        ('xl/worksheets/sheet1.xml',
         '<worksheet xmlns="%s"><sheetData><row><c t="s"><v>0</v></c>'
         '<c t="inlineStr"><is><t>inline</t></is></c></row></sheetData>'
         '</worksheet>' % S),
    ])


def make_pptx(text):
    return _zip([
        ('[Content_Types].xml', '<Types/>'),
        ('ppt/slides/slide1.xml',
         '<p:sld xmlns:p="p" xmlns:a="%s"><a:p><a:r><a:t>%s</a:t></a:r>'
         '</a:p></p:sld>' % (A, text)),
    ])


def make_odf(text, kind='text'):
    return _zip([
        ('mimetype', 'application/vnd.oasis.opendocument.%s' % kind),
        ('content.xml',
         '<office:document-content '
         'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
         'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
         '<office:body><office:text><text:p>%s<text:s/>end</text:p>'
         '</office:text></office:body></office:document-content>' % text),
    ])
