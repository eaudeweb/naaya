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
