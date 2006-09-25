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
# Alexandru Ghica, Finsiel Romania

#Python imports

#Zope imports
from Globals                                    import InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl                              import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions                  import view_management_screens, view

#Product imports
import babelizer
from constants                                      import *
from Products.NaayaBase.constants                   import *
from Products.NaayaContent                          import *
from Products.Naaya.constants                       import *
from Products.NaayaCore.constants                   import *
from Products.NaayaCore.ProfilesTool.ProfileMeta    import ProfileMeta
from Products.Naaya.NySite                          import NySite
from Products.NaayaCore.managers.utils              import utils
from Products.NaayaCore.managers.utils              import file_utils, batch_utils
from Products.NaayaCore.managers.search_tool        import ProxiedTransport
from Products.NaayaCalendar.EventCalendar           import manage_addEventCalendar

manage_addReportSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addReportSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, ReportSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class ReportSite(NySite, ProfileMeta):
    """ """

    meta_type = METATYPE_REPORTSITE
    icon = 'misc_/Report/Site.gif'

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
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)
        #install new objects

        #load site skeleton - configuration
        self.loadSkeleton(join(REPORT_PRODUCT_PATH, 'skel'))

        #set default main topics
        try:    self.getPropertiesTool().manageMainTopics(['info', 'reports'])
        except: pass

    def daysLeft(self, REQUEST=None):
        """ """
        today = self.utGetTodayDate()
        finish = self.utGetDate('30/11/2006')
        days_left = int(finish -today)
        if days_left <= 0:
            return None
        return days_left

    def translate_comment(self, phrase, from_lang='', to_lang='', REQUEST=None):
        """ """
        try:
            print babelizer.translate(phrase, from_lang, to_lang)
            return babelizer.translate(phrase, from_lang, to_lang)
        except:
            return ''

    security.declarePublic('update_images_path')
    def update_images_path(self):
        """ update images path according to the new Epoz update """
        catalog = self.getCatalogTool()

        for sec in catalog.query_objects_ex(meta_type=['Naaya Report Section']):
            for img in sec.objectValues('Image'):
                #image path
                old_path = img.absolute_url(1).replace("/cap", "/rep").replace("/sec", "/rep")
                old_path = old_path.replace("belgrade3", "http://belgrade1.finsiel.ro")
                #new_path = img.absolute_url(1)
                new_path = img.getId()

                #description
                old_descr = sec.getLocalProperty('description', 'en')
                new_descr = old_descr.replace(old_path, new_path)

                #test bad values
                if old_descr.find('src="http://') != -1:
                    #print sec.absolute_url()
                    pass

                #update objects
                sec.save_properties(sec.getLocalProperty('title', 'en'), new_descr, sec.getLocalProperty('coverage', 'en'), 
                    sec.getLocalProperty('keywords', 'en'), sec.sortorder, sec.releasedate, 'en')
                sec._p_changed = 1

        return True

InitializeClass(ReportSite)
