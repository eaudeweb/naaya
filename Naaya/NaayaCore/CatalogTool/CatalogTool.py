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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.ZCatalog import ZCatalog

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
try:
    import Products.TextIndexNG2
    txng_version = 2
except ImportError:
    txng_version = 0

def manage_addCatalogTool(self, languages=None, REQUEST=None):
    """ """
    if languages is None: languages = []
    ob = CatalogTool(ID_CATALOGTOOL, TITLE_CATALOGTOOL)
    self._setObject(ID_CATALOGTOOL, ob)
    self._getOb(ID_CATALOGTOOL).loadDefaultData(languages)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class CatalogTool(ZCatalog, utils):
    """ """

    meta_type = METATYPE_CATALOGTOOL
    icon = 'misc_/NaayaCore/CatalogTool.gif'

    manage_options = (
        ZCatalog.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        #constructor
        ZCatalog.__dict__['__init__'](self, id, title, None, None)
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, languages):
        #creates default indexes and other stuff
        #create indexes
        languages = self.utConvertToList(languages)
        try: self.addIndex('bobobase_modification_time', 'FieldIndex')
        except: pass
        try: self.addIndex('id', 'FieldIndex')
        except: pass
        try: self.addIndex('meta_type', 'FieldIndex')
        except: pass
        try: self.addIndex('path', 'PathIndex')
        except: pass
        if txng_version == 2:
            try: self.manage_addIndex('PrincipiaSearchSource', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'use_converters':1, 'autoexpand':1})
            except: pass
            try: self.manage_addIndex('title', 'TextIndexNG2', extra={'default_encoding': 'utf-8'})
            except: pass
        else:
            try: self.addIndex('PrincipiaSearchSource', 'TextIndex')
            except: pass
            try: self.addIndex('title', 'TextIndex')
            except: pass
        try: self.addIndex('submitted', 'FieldIndex')
        except: pass
        try: self.addIndex('approved', 'FieldIndex')
        except: pass
        try: self.addIndex('topitem', 'FieldIndex')
        except: pass
        try: self.addIndex('checkout', 'FieldIndex')
        except: pass
        try: self.addIndex('validation_status', 'FieldIndex')
        except: pass
        for lang in languages: self.add_indexes_for_lang(lang)
        try: self.addIndex('releasedate', 'FieldIndex')
        except: pass
        #create columns
        try: self.addColumn('id')
        except: pass
        try: self.addColumn('title')
        except: pass
        try: self.addColumn('meta_type')
        except: pass
        try: self.addColumn('bobobase_modification_time')
        except: pass
        try: self.addColumn('releasedate')
        except: pass
        try: self.addColumn('summary')
        except: pass

    security.declarePrivate('add_indexes_for_lang')
    def add_indexes_for_lang(self, lang):
        if txng_version == 2:
            try:
                self.manage_addIndex('objectkeywords_%s' % lang, 'TextIndexNG2', extra={'default_encoding': 'utf-8'})
                self.reindexIndex('objectkeywords_%s' % lang, self.REQUEST)
            except: pass
        else:
            try:
                self.addIndex('objectkeywords_%s' % lang, 'TextIndex')
                self.reindexIndex('objectkeywords_%s' % lang, self.REQUEST)
            except: pass
        try:
            self.addIndex('istranslated_%s' % lang, 'FieldIndex')
            self.reindexIndex('istranslated_%s' % lang, self.REQUEST)
        except: pass

    security.declarePrivate('del_indexes_for_lang')
    def del_indexes_for_lang(self, lang):
        try: self.delIndex('objectkeywords_%s' % lang)
        except: pass
        try: self.delIndex('istranslated_%s' % lang)
        except: pass

InitializeClass(CatalogTool)
