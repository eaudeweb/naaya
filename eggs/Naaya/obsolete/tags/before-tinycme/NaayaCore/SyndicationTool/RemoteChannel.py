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

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.NyFeed import NyFeed

manage_addRemoteChannelForm = PageTemplateFile('zpt/remotechannel_manage_add', globals())
def manage_addRemoteChannel(self, id='', title='', url='', numbershownitems='', portlet='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_SUFIX_REMOTECHANNEL % self.utGenRandomId(6)
    try: numbershownitems = abs(int(numbershownitems))
    except: numbershownitems = 0
    ob = RemoteChannel(id, title, url, numbershownitems)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_remotechannel(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class RemoteChannel(SimpleItem, NyFeed, utils):
    """ """

    meta_type = METATYPE_REMOTECHANNEL
    icon = 'misc_/NaayaCore/RemoteChannel.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'Update information', 'action': 'manage_update_html'},
            {'label': 'Channel data', 'action': 'index_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, url, numbershownitems):
        """ """
        self.id = id
        self.title = title
        self.url = url
        self.numbershownitems = numbershownitems
        NyFeed.__dict__['__init__'](self)

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.delete_portlet_for_object(item)

    #api
    def get_feed_url(self):
        #method from NyFeed
        return self.url

    def set_new_feed_url(self, new_url):
        #method from NyFeed
        self.url = new_url
        self._p_changed = 1

    def getChannelItems(self):
        #returns a list of dictionaries, where a dictionary stores the link and the title of the item
        l = map(lambda x: ({'link': x['link'], 'title': x['title']}), self.get_feed_items())
        if self.numbershownitems > 0: return l[:self.numbershownitems]
        else: return l

    def getChannelItems_complete(self):
        #returns a list of dictionaries, where a dictionary stores the link and the title of the item
        try:
            try: l = map(lambda x: ({'link': x['link'], 'title': x['title'], 'summary': x['summary'], 'date': x['modified']}), self.get_feed_items())
            except: l = map(lambda x: ({'link': x['link'], 'title': x['title'], 'date': x['modified']}), self.get_feed_items())
        except:
            l = map(lambda x: ({'link': x['link'], 'title': x['title']}), self.get_feed_items())
        if self.numbershownitems > 0: return l[:self.numbershownitems]
        else: return l
    def getAllChannelItems(self):
        #returns a list of dictionaries, where a dictionary stores the link and the title of the item
        try:
            try: l = map(lambda x: ({'link': x['link'], 'title': x['title'], 'date': x['modified'], 'summary': x['summary']}), self.get_feed_items())
            except: l = map(lambda x: ({'link': x['link'], 'title': x['title'], 'date': x['modified']}), self.get_feed_items())
        except:
            l = map(lambda x: ({'link': x['link'], 'title': x['title']}), self.get_feed_items())
        return l
    def updateChannel(self, uid):
        """ """
        if uid==self.get_site_uid():
            self.harvest_feed(self.http_proxy)
            if self.get_feed_bozo_exception() is not None: error = self.get_feed_bozo_exception()
            else: error = ''
            return str(error)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', url='', numbershownitems='', REQUEST=None):
        """ """
        try: numbershownitems = abs(int(numbershownitems))
        except: numbershownitems = self.numbershownitems
        self.title = title
        self.url = url
        self.numbershownitems = numbershownitems
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    #zmi forms
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/remotechannel_properties', globals())

    security.declareProtected(view_management_screens, 'manage_update_html')
    manage_update_html = PageTemplateFile('zpt/remotechannel_update', globals())

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/remotechannel_index', globals())

InitializeClass(RemoteChannel)
