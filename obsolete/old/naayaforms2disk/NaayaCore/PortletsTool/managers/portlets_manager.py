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
# The Original Code is Naaya version 1.0
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

#Product imports
from Products.NaayaCore.constants import *

class portlets_manager:
    """ """

    def __init__(self):
        self.__left_portlets_ids = []
        self.__center_portlets_ids = []
        self.__right_portlets_locations = {}

    #api
    def get_left_portlets_ids(self): return self.__left_portlets_ids
    def get_center_portlets_ids(self): return self.__center_portlets_ids
    def get_right_portlets_locations(self, p_filter=None):
        #get the collection appling the filter if present
        #it is a path filter
        if p_filter:
            r = {}
            for k, v in self.__right_portlets_locations.items():
                if k.startswith(p_filter):
                    r[k] = v
            return r
        else:
            return self.__right_portlets_locations

    def set_left_portlets_ids(self, p_ids):
        self.__left_portlets_ids = p_ids
        self._p_changed = 1

    def set_center_portlets_ids(self, p_ids):
        self.__center_portlets_ids = p_ids
        self._p_changed = 1

    def set_right_portlets_locations(self, p_location, p_ids):
        if len(p_ids) == 0:
            try: del(self.__right_portlets_locations[p_location])
            except: pass
        else:
            self.__right_portlets_locations[p_location] = p_ids
        self._p_changed = 1

    def delete_right_portlets_locations(self, p_location, p_id):
        if self.__right_portlets_locations.has_key(p_location):
            try: self.__right_portlets_locations[p_location].remove(p_id)
            except: pass
            if len(self.__right_portlets_locations[p_location]) == 0:
                try: del(self.__right_portlets_locations[p_location])
                except: pass
        self._p_changed = 1

    def get_available_left_portlets_objects(self):
        #returns a list with available left portlets object
        ids = self.utListDifference(self.getPortletsTool().getPortletsIds(), self.__left_portlets_ids)
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, ids, (None,)*len(ids)))

    def get_left_portlets_objects(self):
        #get the left portlets objects
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, self.__left_portlets_ids, (None,)*len(self.__left_portlets_ids)))

    def get_available_center_portlets_objects(self):
        #returns a list with available center portlets object
        ids = self.utListDifference(self.getPortletsTool().getPortletsIds(), self.__center_portlets_ids)
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, ids, (None,)*len(ids)))

    def get_center_portlets_objects(self):
        #get the center portlets objects
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, self.__center_portlets_ids, (None,)*len(self.__center_portlets_ids)))

    def get_available_right_locations_objects(self, p_location):
        #returns a list with available right portlets object
        ids = self.utListDifference(self.getPortletsTool().getPortletsIds(), self.__right_portlets_locations.get(p_location, []))
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, ids, (None,)*len(ids)))

    def get_right_portlets_locations_objects(self, p_location=None):
        #get the right portlets objects
        if p_location is None or p_location is self: portlets_ids = self.__right_portlets_locations.get('', [])
        else: 
            portlets_ids = []
            for i in self.getAllParents(p_location):
                portlets_ids.extend(self.__right_portlets_locations.get(i.absolute_url(1), []))
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, portlets_ids, (None,)*len(portlets_ids)))

    def get_portlet_object(self, p_id):
        #returns a portlet object with the given id
        return self.getPortletsTool()._getOb(p_id, None)

    def delete_portlet_for_object(self, ob):
        #try to delete the portlet for the given object
        #if the portlet was manually renamed or deleted an error will occour
        try: self.getPortletsTool()._delObject('%s%s' % (PREFIX_PORTLET, ob.id))
        except: pass

    def exists_portlet_for_object(self, ob):
        #test if there is a portlet for the given object
        return '%s%s' % (PREFIX_PORTLET, ob.id) in self.getPortletsTool().getPortletsIds()

    #special
    def create_portlet_special(self, portlet_id, portlet_title, content):
        #create special portlet with a default content
        portlets_ob = self.getPortletsTool()
        portlet_ob = portlets_ob._getOb(portlet_id, None)
        if portlet_ob is None:
            portlets_ob.addPortlet(portlet_id, portlet_title, 100)
            portlet_ob = portlets_ob._getOb(portlet_id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #links list
    def create_portlet_for_linkslist(self, linkslist_ob):
        #create a portlet for this links list object using the specific template, TYPE = 1
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, linkslist_ob.id)
        portlets_ob.addPortlet(portlet_id, linkslist_ob.title_or_id(), 1)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_LINKSLIST_ID', linkslist_ob.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #remote channel
    def create_portlet_for_remotechannel(self, channel_ob):
        #create a portlet for this remote channel using the specific template, TYPE = 2
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, channel_ob.id)
        portlets_ob.addPortlet(portlet_id, channel_ob.title_or_id(), 2)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_REMOTECHANNEL_ID', channel_ob.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #remote channel facade
    def create_portlet_for_remotechannelfacade(self, channel_ob):
        #create a portlet for this remote channel facade using the specific template, TYPE = 6
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, channel_ob.id)
        portlets_ob.addPortlet(portlet_id, channel_ob.title_or_id(), 6)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_REMOTECHANNEL_ID', channel_ob.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #remote channels aggregator
    def create_portlet_for_remotechannels_aggregator(self, aggregator_ob):
        #create a portlet for this aggregator using the specific template, TYPE = 7
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, aggregator_ob.id)
        portlets_ob.addPortlet(portlet_id, aggregator_ob.title_or_id(), 7)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_AGGREGATOR_ID', aggregator_ob.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #local channel
    def create_portlet_for_localchannel(self, channel_ob):
        #create a portlet for this channel using the specific template, TYPE = 3
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, channel_ob.id)
        portlets_ob.addPortlet(portlet_id, channel_ob.title_or_id(), 3)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_LOCALCHANNEL_ID', channel_ob.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #folder
    def create_portlet_for_folder(self, folder_ob):
        #create a portlet for this folder using the specific template, TYPE = 4
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, folder_ob.id)
        portlets_ob.addPortlet(portlet_id, folder_ob.title_or_id(), 4)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_FOLDER_PATH', folder_ob.absolute_url(1))
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #script channel
    def create_portlet_for_scriptchannel(self, channel_ob):
        #create a portlet for this channel using the specific template, TYPE = 5
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, channel_ob.id)
        portlets_ob.addPortlet(portlet_id, channel_ob.title_or_id(), 5)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = portlet_ob.document_src().replace('PORTLET_SCRIPTCHANNEL_ID', channel_ob.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')
