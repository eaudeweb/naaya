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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports

#Zope imports
from Globals                                    import InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view

#Product imports
from constants                                      import *
from Products.NaayaBase.constants                   import *
from Products.NaayaContent                          import *
from Products.Naaya.constants                       import *
from Products.NaayaCore.constants                   import *
from Products.NaayaCore.ProfilesTool.ProfileMeta    import ProfileMeta
from Products.Naaya.NySite                          import NySite
from Products.NaayaCore.managers.utils              import utils, file_utils, batch_utils


manage_addSMAPSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addSMAPSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, SMAPSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class SMAPSite(NySite, ProfileMeta):
    """ """

    meta_type = METATYPE_SMAPSITE
    icon = 'misc_/SMAP/Site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #load site skeleton - configuration
        self.loadSkeleton(join(SMAP_PRODUCT_PATH, 'skel'))

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')
        self.manage_delObjects('info')

        #set default 'Main topics'
        try:    self.getPropertiesTool().manageMainTopics(['smap', 'contact'])
        except: pass

    #layer over selection lists
    security.declarePublic('getCountriesList')
    def getCountriesList(self):
        """
        Return the selection list for countries.
        """
        return self.getPortletsTool().getRefListById('countries').get_list()

    security.declarePublic('getCountryName')
    def getCountryName(self, id):
        """
        Return the title of an item for the selection list for countries.
        """
        try:
            return self.getPortletsTool().getRefListById('countries').get_item(id).title
        except:
            return ''
        
    security.declarePublic('getPrioritiesTypesList')
    def getPrioritiesTypesList(self):
        """
        Return the selection list for priorities types.
        """
        return self.getPortletsTool().getRefListById('priorities_types').get_list()

    security.declarePublic('getPriorityTitle')
    def getPriorityTitle(self, id):
        """
        Return the title of an item for the selection list for priorities types.
        """
        try:
            return self.getPortletsTool().getRefListById('priorities_types').get_item(id).title
        except:
            return ''
        
    security.declarePublic('getFocusesTypesList')
    def getFocusesTypesList(self):
        """
        Return the selection list for focuses types.
        """
        return self.getPortletsTool().getRefListById('focuses_types').get_list()

    security.declarePublic('getFocusTitle')
    def getFocusTitle(self, id):
        """
        Return the title of an item for the selection list for focuses types.
        """
        try:
            return self.getPortletsTool().getRefListById('focuses_types').get_item(id).title
        except:
            return ''

    #Naaya wrapper
    security.declarePublic('isRTL')
    def isRTL(self, lang=None):
        """ test if lang is a RTL language """
        return self.isArabicLanguage(lang)

    #objects getters
    def getSkinFilesPath(self): return self.getLayoutTool().getSkinFilesPath()

InitializeClass(SMAPSite)
