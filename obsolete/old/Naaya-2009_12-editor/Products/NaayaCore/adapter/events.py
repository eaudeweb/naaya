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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#   Cornel Nitu, Eau de Web

from zope.app.container.interfaces import IObjectRemovedEvent

#
# LinksList
#
def removedLinksList(ob, event):
    """ A LinksList was removed """
    ob.delete_portlet_for_object(ob)

#
# LocalChannel
#
def removedLocalChannel(ob, event):
    """ A LocalChannel was removed """
    ob.delete_portlet_for_object(ob)

#
# RemoteChannel
#
def removedRemoteChannel(ob, event):
    """ A RemoteChannel was removed """
    ob.delete_portlet_for_object(ob)

#
# ScriptChannel
#
def removedScriptChannel(ob, event):
    """ A ScriptChannel was removed """
    ob.delete_portlet_for_object(ob)

#
# ChannelAggregator
#
def removedChannelAggregator(ob, event):
    """ A ChannelAggregator was removed """
    ob.delete_portlet_for_object(ob)

#
# DynamicPropertiesItem
#
def removedDynamicPropertiesItem(ob, event):
    """ A DynamicPropertiesItem was removed """
    ids = ob.getDynamicPropertiesIds()
    for item in ob.getCatalogedObjects(ob.id):
        map(item.deleteProperty, ids)

def modifiedDynamicPropertiesItem(obj, event):
    if not IObjectRemovedEvent.providedBy(event):
        #a DynamicPropertiesItem was added
        l_dp_dict = {}
        lang = obj.gl_get_selected_language()
        for dp in obj.getDynamicProperties():
            l_dp_dict[dp.id] = dp.defaultvalue
        for item in obj.getCatalogedObjects(obj.id):
            item.createDynamicProperties(l_dp_dict, lang)
