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
# The Initial Owner of the Original Code is EEA.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Eau de Web
# Cornel Nitu, Eau de Web
# Miruna Badescu, Eau de Web

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product related imports
from Products.Report.tools.constants import *
from managers.rate_manager import rate_manager

manage_addRateListForm = PageTemplateFile('zpt/ratelist_add', globals())
def manage_addRateList(self, id='', title='', description='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_SUFIX_REFLIST % self.utGenRandomId(6)
    ob = RateList(id, title, description)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class RateList(SimpleItem, rate_manager):
    """ """

    meta_type = METATYPE_RATELIST
    icon = 'misc_/Report/RateList.gif'

    manage_options = (
        (
            {'label': 'Items', 'action': 'manage_items_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, description):
        """ """
        self.id = id
        self.title = title
        self.description = description
        rate_manager.__dict__['__init__'](self)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    security.declareProtected(view_management_screens, 'manage_add_item')
    def manage_add_item(self, id='', title='', REQUEST=None):
        """ """
        self.add_item(id, title)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_items_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_update_item')
    def manage_update_item(self, id='', title='', REQUEST=None):
        """ """
        self.update_item(id, title)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_items_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_delete_items')
    def manage_delete_items(self, ids=[], REQUEST=None):
        """ """
        self.delete_item(self.utConvertToList(ids))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_items_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_items_html')
    manage_items_html = PageTemplateFile('zpt/ratelist_items', globals())

InitializeClass(RateList)