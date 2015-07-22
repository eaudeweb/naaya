from ZPublisher import BeforeTraverse
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent

#
# NySite
#
def addedNySite(ob, event):
    """ A NySite was added """
    handle = ob.meta_type + '/' + ob.getId()
    nc = BeforeTraverse.NameCaller(ob.getId())
    BeforeTraverse.registerBeforeTraverse(ob, nc, handle)

def removedNySite(ob, event):
    """ A NySite was removed """
    handle = ob.meta_type + '/' + ob.getId()
    BeforeTraverse.unregisterBeforeTraverse(ob, handle)

def movedNySite(ob, event):
    """ A NySite was moved """
    if IObjectAddedEvent.providedBy(event):

        #Hadled by addedNySite
        return
    elif IObjectRemovedEvent.providedBy(event):

        #Hadled by removedNySite
        return
    else:
        old_handle = ob.meta_type + '/' + event.oldName
        BeforeTraverse.unregisterBeforeTraverse(ob, old_handle)
        handle = ob.meta_type + '/' + event.newName
        nc = BeforeTraverse.NameCaller(event.newName)
        BeforeTraverse.registerBeforeTraverse(ob, nc, handle)
        #TODO: ONLY when copy/paste, catalog should be updated to remove references to old (existing) object

#
# NyFolder
#
def removedNyFolder(ob, event):
    """ A NyFolder was removed """
    ob.delete_portlet_for_object(ob)
