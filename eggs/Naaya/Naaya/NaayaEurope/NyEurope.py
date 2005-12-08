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
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaEurope.constants import *
from Products.NaayaBase.constants import *
from managers.country_manager import country_manager

def manage_addNyEurope(self, REQUEST=None):
    """ """
    ob = NyEurope(ID_NYEUROPE, TITLE_NYEUROPE)
    self._setObject(ID_NYEUROPE, ob)
    self._getOb(ID_NYEUROPE).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NyEurope(SimpleItem, country_manager):
    """ """

    meta_type = METATYPE_NYEUROPE
    icon = 'misc_/NaayaEurope/NyEurope.gif'

    manage_options = (
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        country_manager.__dict__['__init__'](self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        portletstool_ob = self.getPortletsTool()
        reflist_ob = portletstool_ob._getOb(ID_REFLIST, None)
        if reflist_ob is None:
            portletstool_ob.manage_addRefList(ID_REFLIST, TITLE_REFLIST, '')
            reflist_ob = portletstool_ob._getOb(ID_REFLIST)
        for line in open(join(NAAYAEUROPE_PRODUCT_PATH, 'data', 'europe.txt'), 'r').readlines():
            line = line.strip()
            if line != '':
                code, name = line.split('\t')
                reflist_ob.add_item(code, name)

    #overwrite handlers
    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        try: self.getPortletsTool()._delObject(ID_REFLIST)
        except: pass

    #layer over selection lists
    security.declarePublic('getCountriesList')
    def getEuropeCountriesList(self):
        """
        Return the selection list for Europe countries.
        """
        return self.getPortletsTool().getRefListById(ID_REFLIST).get_list()

    def getEuropeCountryTitle(self, id):
        """
        Return the title of an item for the selection list for Europe countries.
        """
        try:
            return self.getPortletsTool().getRefListById(ID_REFLIST).get_item(id).title
        except:
            return ''

    #xml-rpc interface for the flash application
    security.declarePublic('get_europe_countries')
    def get_europe_countries(self):
        """
        Returns two lists, one with country codes and one with names.
        """
        l = self.getEuropeCountriesList()
        return [x.id for x in l], [x.title for x in l]

    def get_europe_countries_in_network(self):
        """
        Returns a list with countries with a portal and in network.
        """
        pass

    security.declarePublic('get_europe_country_info')
    def get_europe_country_info(self, code):
        """
        Returns a list with country properties.
        """
        c = self.get_item(code)
        if c is not None:
            return [self.getEuropeCountryTitle(c.id), c.organisation, c.contact, c.url, c.host]
        else:
            return ['', '', '', '', '']

    #administration actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addcountry')
    def admin_addcountry(self, country='', organisation='', contact='', url='', host='', REQUEST=None):
        """ """
        self.add_item(country, country, organisation, contact, url, host)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_countries_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_editcountry')
    def admin_editcountry(self, country='', organisation='', contact='', url='', host='', REQUEST=None):
        """ """
        self.update_item(country, country, organisation, contact, url, host)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_countries_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_deletecountry')
    def admin_deletecountry(self, ids=[], REQUEST=None):
        """ """
        self.delete_item(self.utConvertToList(ids))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_countries_html' % self.absolute_url())

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_countries_html')
    admin_countries_html= PageTemplateFile('zpt/europe_admin_countries', globals())

InitializeClass(NyEurope)
