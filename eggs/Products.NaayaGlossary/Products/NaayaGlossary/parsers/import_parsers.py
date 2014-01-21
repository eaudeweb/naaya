# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Ghica Alexandru, Finsiel Romania


#product imports
from DateTime import DateTime
from Globals import MessageDialog
from Products.NaayaGlossary.constants import NAAYAGLOSSARY_ELEMENT_METATYPE
from Products.NaayaGlossary.constants import NAAYAGLOSSARY_FOLDER_METATYPE
from Products.NaayaGlossary.parsers.tmx_parser import tmx_parser
#from Products.NaayaGlossary.utils import utils
#from cStringIO import StringIO
from naaya.core.zope2util import ofs_path
from types import UnicodeType   #, StringType
#from xml.sax import handler     # InputSource    # make_parser,
import string

def escape(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').\
        replace("'", '&apos;').replace('<', '&lt;').replace('>', '&gt;')


class glossary_export:
    """ """

    def __init__(self):
        """ constructor """

    def xliff_http_header(self, RESPONSE):
        """ set the HTTP headers for xliff export """
        RESPONSE.setHeader('Content-Type', 'application/data; charset=UTF-8')
        language = self.REQUEST.form.get('language', 'English')
        filename = '"%s_%s.xliff"' % (self.id, language)
        RESPONSE.setHeader('Content-Disposition',
                           'attachment; filename=' + filename)

    def xliff_header(self, folders, language):
        """ return the xliff header """

        results = []
        r_append = results.append   #alias for append function. For optimization purposes
        # Generate the XLIFF file header
        if folders == '/':
            folders='all'
        else:
            folders = string.split(folders, '/')[-1]
        r_append('<?xml version="1.0" encoding="UTF-8"?>')
        r_append('<!DOCTYPE xliff SYSTEM "http://www.oasis-open.org/committees/xliff/documents/xliff.dtd">')
        r_append(u'<!-- XLIFF Format Copyright \xa9 OASIS Open 2001-2003 -->')
        r_append('<xliff version="1.0">')
        r_append('<file')
        r_append(' original="%s"' % ofs_path(self))
        r_append(' product-name="NaayaGlossary"')
        r_append(' product-version="1.1.x"')
        r_append(' datatype="plaintext"')
        r_append(' source-language="English"')
        r_append(' target-language="%s"' % language)
        r_append(' date="%s"' % DateTime().HTML4())
        r_append('>')
        r_append('<body>')
        return results

    def xliff_footer(self):
        results = []
        r_append = results.append   #alias for append function. For optimization purposes
        r_append('</body>')
        r_append('</file>')
        r_append('</xliff>')
        return results

    def xliff_export(self, folder='', language='',
                     published=0, empty_folders=False, REQUEST=None):
        """ Exports the content to an XLIFF file """
        results_list = []
        results = []
        terms = []
        r_append = results_list.append   #alias for append function. For optimization purposes

        trans_unit_template = '\r\n'.join([
            '<trans-unit id="%(term_id)s" approved="%(approved)s">',
            '<source>%(source_trans)s</source>',
            '<target>%(target_trans)s</target>',
            '<context-group name="%(folder_id)s">%(folder_trans)s</context-group>',
            '<note>%(def_trans)s</note>',
            '</trans-unit>',
        ])

        if not folder:
            folder = ofs_path(self)

        if not published:
            terms.extend(self.get_published('/%s' % folder))
        else:
            terms.extend(self.get_all_objects('/%s' % folder))
        results_list.extend(self.xliff_header(folder, language))
        for term in terms:
            term.get_translation_by_language('English')
            #translation = term.get_translation_by_language(language)
            if language in self.get_unicode_langs():
                translation = self.convertWinCodesToHTMLCodes(term.get_translation_by_language(language))
            else:
                translation = term.get_translation_by_language(language)

            l_folder = term.aq_parent
            while l_folder.aq_parent != self:
                l_folder = l_folder.aq_parent

            r_append(trans_unit_template % {
                'term_id': term.id,
                'approved': term.approved,
                'source_trans': escape(term.get_translation_by_language('English')),
                'target_trans': escape(translation),
                'def_trans': escape(term.get_def_trans_by_language(language)),
                'folder_id': l_folder.id,
                'folder_trans': escape(l_folder.get_translation_by_language(language)),
            })

        if empty_folders:
            for l_folder in self.objectValues([NAAYAGLOSSARY_FOLDER_METATYPE]):
                if l_folder.objectIds([NAAYAGLOSSARY_ELEMENT_METATYPE]):
                    continue # it's not empty
                r_append(trans_unit_template % {
                    'term_id': '%s_dummy' % l_folder.id,
                    'approved': '1',
                    'source_trans': "",
                    'target_trans': "",
                    'def_trans': "",
                    'folder_id': l_folder.id,
                    'folder_trans': l_folder.get_translation_by_language(language),
                })

        results_list.extend(self.xliff_footer())

        for x in results_list:
            if type(x) is UnicodeType: results.append(x.encode('utf-8'))
            else:                      results.append(x)

        if REQUEST is not None:
            self.xliff_http_header(REQUEST.RESPONSE)

        return '\r\n'.join(results)

    def tmx_export(self, folder='/', published=0, REQUEST=None):
        """ Exports the content to a TMX file """
        results = []
        results_list=[]
        terms=[]
        r_append = results_list.append
        if not published:
            terms.extend(self.get_published('/%s' % folder))
        else:
            terms.extend(self.get_all_objects('/%s' % folder))

        results_list.extend(self.tmx_header(folder))

        for term in terms:
            r_append('<tu tuid="%s">' % term.id)
            for language in self.get_english_names():
                translation = term.get_translation_by_language(language)
                if language in self.get_unicode_langs():
                    r_append('<tuv xml:lang="%s">' % language)
                    r_append('<seg>%s</seg></tuv>' % self.convertWinCodesToHTMLCodes(translation))
                else:
                    r_append('<tuv xml:lang="%s">' % language)
                    r_append('<seg>%s</seg></tuv>' % translation)
            r_append('</tu>')
            r_append('')

        results_list.extend(self.tmx_footer())
        for x in results_list:
            if type(x) is UnicodeType: results.append(x.encode('utf-8'))
            else:                      results.append(x)
        return '\r\n'.join(results)

    def tmx_header(self, folders):
        """ return the tmx header """
        r=[]
        r_append = r.append
        if folders == '/':
            folders='all'
        else:
            folders = string.split(folders, '/')[-1]
        self.REQUEST.RESPONSE.setHeader('Content-type', 'application/data; charset=UTF-8')
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s_%s.tmx"' % (self.id, folders))
        r_append('<?xml version="1.0" encoding="utf-8"?>')
        r_append('<!DOCTYPE tmx SYSTEM "http://www.lisa.org/tmx/tmx14.dtd">')
        r_append('<tmx version="1.4">')
        r_append('<header')
        r_append(' creationtool="NaayaGlossary"')
        r_append(' creationtoolversion="1.x"')
        r_append(' datatype="plaintext"')
        r_append(' segtype="paragraph"')
        r_append(' adminlang="English"')
        r_append(' srclang="English"')
        r_append(' o-encoding="utf-8"')

        r.append('>')
        r.append('</header>')
        r.append('<body>')
        r.append('')
        return r

    def tmx_footer(self):
        """ return the tmx footer """
        r=[]
        r_append = r.append
        r_append('</body>')
        r_append('</tmx>')
        return r

    ##################
    #   tmx import   #
    ##################

    def tmx_import(self, file, REQUEST=None):
        """ Imports a TMX file """

        import string
        #from xml.sax import make_parser, handler, InputSource
        #from cStringIO import StringIO

        parser = tmx_parser()

        #parse the tmx information
        chandler = parser.parseContent(file)

        if chandler is None:
            return MessageDialog(title = 'Parse error',
             message = 'Unable to parse TMX file' ,  action = 'manage_main',)

        l_list = chandler.TMXContent.keys()
        l_list.sort()
        for k in l_list:
            folder_id = self.utf8_to_latin1(string.upper(k[:1]))
            folder = self.unrestrictedTraverse(folder_id, None)
            if folder is None:
                try:
                    self.manage_addGlossaryFolder(folder_id, '', [], '', '', 1)
                    folder = self._getOb(folder_id)
                except Exception:   #, error:
                    #print error
                    pass
            elem_ob = folder._getOb(k, None)
            if elem_ob is not None:
                for lang,trans in chandler.TMXContent[k].items():
                    if trans != '':
                        elem_ob.set_translations_list(lang, trans.encode('utf-8'))
                elem_ob.cu_recatalog_object(elem_ob)
            else:
                try:
                    elem_name = self.utf8_to_latin1(chandler.TMXContent[k]['English'])
                    folder.manage_addGlossaryElement(elem_name, elem_name, '', [], '', 1)
                except Exception:   #, error
                    #print error
                    pass
                elem_ob = folder._getOb(elem_name, None)
                if elem_ob is not None:
                    for lang,trans in chandler.TMXContent[k].items():
                        elem_ob.set_translations_list(lang, trans.encode('utf-8'))
                    elem_ob.cu_recatalog_object(elem_ob)
