# -*- coding=utf-8 -*-

# Python imports
import time
from datetime import datetime
from io import StringIO
from lxml import etree

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

# Project imports
from naaya.i18n.ImportExport import TranslationsImportExport
from naaya.i18n.NyMessageCatalog import NyMessageCatalog


def xml_equal(xml1, xml2):
    """Compare two XML strings structurally (ignoring attribute order)."""
    tree1 = etree.fromstring(xml1.encode('utf-8') if isinstance(xml1, str) else xml1)
    tree2 = etree.fromstring(xml2.encode('utf-8') if isinstance(xml2, str) else xml2)
    return _elements_equal(tree1, tree2)


def _element_sort_key(e):
    return (e.tag, e.get('tuid', ''), e.get('id', ''),
            e.get('{http://www.w3.org/XML/1998/namespace}lang', e.get('lang', '')),
            (e.text or '').strip())


def _elements_equal(e1, e2):
    if e1.tag != e2.tag:
        return False
    if (e1.text or '').strip() != (e2.text or '').strip():
        return False
    if (e1.tail or '').strip() != (e2.tail or '').strip():
        return False
    if dict(e1.attrib) != dict(e2.attrib):
        return False
    if len(e1) != len(e2):
        return False
    children1 = sorted(e1, key=_element_sort_key)
    children2 = sorted(e2, key=_element_sort_key)
    return all(_elements_equal(c1, c2) for c1, c2 in zip(children1, children2))

expected_po_en = lambda: ("""msgid ""
msgstr "Project-Id-Version: naaya.i18n\\n"
"POT-Creation-Date: %(cdate)s\\n"
"PO-Revision-Date: %(cdate)s\\n"
"Last-Translator:  <>\\n"
"Language-Team: en <>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"


msgid "${x} <b>\\"apples\\"</b>"
msgstr "${x} <b>\\"apples\\"</b>"

msgid "Administration"
msgstr "Administration"
""" % {'cdate': time.strftime('%Y-%m-%d %H:%M+%Z', time.gmtime(time.time()))})


expected_po_de = lambda: ("""msgid ""
msgstr "Project-Id-Version: naaya.i18n\\n"
"POT-Creation-Date: %(cdate)s\\n"
"PO-Revision-Date: %(cdate)s\\n"
"Last-Translator:  <>\\n"
"Language-Team: de <>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"


msgid "${x} <b>\\"apples\\"</b>"
msgstr "${x} <b>\\"Äpfel\\"</b>"

msgid "Administration"
msgstr "Verwaltung"
""" % {'cdate': time.strftime('%Y-%m-%d %H:%M+%Z', time.gmtime(time.time()))})


expected_xliff_de = lambda: ("""<?xml version='1.0' encoding='utf-8'?>
<xliff version="1.0">
  <file datatype="plaintext" product-version="1.0" date="%(cdate)s" source-language="en" product-name="naaya.i18n" target-language="de"/>
  <header></header>
  <body>
    <trans-unit approved="yes" id="%(id_apple)s">
      <source>${x} &lt;b&gt;"apples"&lt;/b&gt;</source>
      <target xml:lang="de">${x} &lt;b&gt;"Äpfel"&lt;/b&gt;</target>
    </trans-unit>
    <trans-unit approved="yes" id="%(id_admin)s">
      <source>Administration</source>
      <target xml:lang="de">Verwaltung</target>
    </trans-unit>
  </body>
</xliff>
""" % {'cdate': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
               'id_apple': '2a498064a922f465264242a8f71d8f3d',
               'id_admin': '7258e7251413465e0a3eb58094430bde'})

expected_tmx = lambda: ("""<?xml version='1.0' encoding='UTF-8'?>
<tmx version="1.4">
  <header adminlang="en" o-encoding="utf-8" datatype="xml" creationtoolversion="1.0" creationtool="naaya.i18n" srclang="en" segtype="block"></header>
  <body>
    <tu creationdate="%(cdate)s" creationtoolversion="1.0" creationtool="naaya.i18n" tuid="%(id_apple)s">
      <tuv creationdate="%(cdate)s" xml:lang="de">
        <seg>${x} &lt;b&gt;"Äpfel"&lt;/b&gt;</seg>
      </tuv>
      <tuv creationdate="%(cdate)s" xml:lang="en">
        <seg>${x} &lt;b&gt;"apples"&lt;/b&gt;</seg>
      </tuv>
    </tu>
    <tu creationdate="%(cdate)s" creationtoolversion="1.0" creationtool="naaya.i18n" tuid="%(id_admin)s">
      <tuv creationdate="%(cdate)s" xml:lang="de">
        <seg>Verwaltung</seg>
      </tuv>
      <tuv creationdate="%(cdate)s" xml:lang="en">
        <seg>Administration</seg>
      </tuv>
    </tu>
  </body>
</tmx>
""" % {'cdate': datetime.now().strftime("%Y%m%dT%H%M%SZ"),
       'id_apple': '2a498064a922f465264242a8f71d8f3d',
       'id_admin': '7258e7251413465e0a3eb58094430bde'})

class ImportExportTestSuite(NaayaTestCase):

    def setUp(self):
        self.catalog = NyMessageCatalog('id', 'title', ('en', 'de'))
        self.tool = TranslationsImportExport(self.catalog)
        self.catalog.edit_message('Administration', 'de', 'Verwaltung')
        self.catalog.edit_message('${x} <b>"apples"</b>', 'de',
                                  u'${x} <b>"Äpfel"</b>')

    def test_export_po(self):
        exported = self.tool.export_po('en')
        self.assertEqual(exported, expected_po_en())
        exported = self.tool.export_po('de')
        self.assertEqual(exported, expected_po_de())

    def test_export_xliff(self):
        exported = self.tool.export_xliff('de')
        self.assertTrue(xml_equal(exported, expected_xliff_de()),
                        'XLIFF export mismatch')

    def test_export_tmx(self):
        exported = self.tool.export_tmx()
        self.assertTrue(xml_equal(exported, expected_tmx()),
                        'TMX export mismatch')

    def test_export_import(self):
        exported = self.tool.export_po('de')
        self.assertEqual(exported, expected_po_de())
        self.catalog.clear()
        bytestream = StringIO(exported)
        self.tool.import_po('de', bytestream)
        self.assertEqual(self.catalog.gettext('Administration', 'de'),
                         'Verwaltung')
        self.assertTrue(self.catalog.gettext('${x} <b>"apples"</b>', 'de') ==
                         u'${x} <b>"Äpfel"</b>')
