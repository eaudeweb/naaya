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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from time import time
import sys
import os, popen2

#Zope imports
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG
from Products.PageTemplates.GlobalTranslationService import setGlobalTranslationService

#Product imports
from Products.NaayaCore.TranslationsTool.TranslationsTool import TranslationsTool
from Products.Localizer.LocalPropertyManager import LocalPropertyManager

#patch for Localizer
def _setLocalPropValue(self, id, lang, value):
    # Get previous value
    old_value, timestamp = self.get_localproperty(id, lang)
    # Update value only if it is different
    if value != old_value:
        properties = self._local_properties.copy()
        if not properties.has_key(id):
            properties[id] = {}
        properties[id][lang] = (value, time())
        self._local_properties = properties

LocalPropertyManager._setLocalPropValue = _setLocalPropValue

class GlobalTranslationService:
    def translate(self, domain, msgid, *args, **kw):
        if domain == 'default':
            domain = 'portal_translations'
        context = kw.get('context')
        if context is None: return msgid
        translation_service = getattr(context, domain, None)
        if translation_service is not None:
            if isinstance(translation_service, TranslationsTool):
                return translation_service.translate(domain, msgid, *args, **kw)
        return msgid

def initialize(context):
    """ """
    setGlobalTranslationService(GlobalTranslationService())

LOG('naayaHotfix', DEBUG, 'Patch for Localizer and other stuff')

#patch for TextIndexNG2. 
from Products.TextIndexNG2.converters import doc, ppt, ps, ooffice, pdf, xls
from Products.TextIndexNG2.Registry import ConverterRegistry

def doc_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'utf-8'
doc.Converter.convert2 = doc_convert2

def ppt_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'iso-8859-15'
ppt.Converter.convert2 = ppt_convert2

def ps_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'iso-8859-15'
ps.Converter.convert2 = ps_convert2

def oo_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'utf-8'
ooffice.Converter.convert2 = oo_convert2

def pdf_convert2(self, doc, encoding, mimetype):
    """Convert pdf data to raw text"""
    tmp_name = self.saveFile(doc)
    if encoding:
        return self.execute('pdftotext -enc UTF-8 "%s" -' % tmp_name), encoding
    return self.execute('pdftotext -enc UTF-8 "%s" -' % tmp_name), 'utf-8'
pdf.Converter.convert2 = pdf_convert2

def xls_convert(self, doc):
    """Convert Excel document to raw text"""
    tmp_name = self.saveFile(doc)
    if sys.platform == 'win32':
        return self.execute('xls2csv -d UTF-8 -q 0 "%s" 2> nul:' % tmp_name)
    else:
        return self.execute('xls2csv -d UTF-8 -q 0 "%s" 2> /dev/null' % tmp_name)
xls.Converter.convert = xls_convert

def xls_convert2(self, doc, encoding, mimetype):
    if encoding:
        return self.convert(doc), encoding
    return self.convert(doc), 'iso-8859-15'
xls.Converter.convert2 = xls_convert2

LOG('naayaHotfix', DEBUG, 'TextIndexNG2 patched')

depends_on = 'ppthtml'
ppt.Converter.depends_on = depends_on

cv = 'ppt'
converter = ppt.Converter()

depends_on = getattr(converter, 'depends_on', None)
if depends_on and os.name == 'posix':
    PO =  popen2.Popen3('which %s' % depends_on)
    out = PO.fromchild.read()
    PO.wait()
    del PO
    if out.find('no %s' % depends_on) > - 1 or out.lower().find('not found') > -1 or len(out.strip()) == 0:
        LOG('naayaHotfix', WARNING, 'Converter "%s" not registered because executable "%s" could not be found' % (cv, depends_on))

for t in converter.getType():
    try:
        ConverterRegistry.register(t, converter)
        LOG('naayaHotfix', INFO, 'Converter "%s" for %s registered' % (cv, t))
    except:
        LOG('naayaHotfix', INFO, 'Converter "%s" for %s NOT registered' % (cv, t))
