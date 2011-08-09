""" Events
"""

from zope import event as zope_event
from OFS.event import ObjectWillBeRemovedEvent, ObjectClonedEvent
from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent
from zope.app.container.contained import (ObjectMovedEvent,
                                          ObjectRemovedEvent,
                                          ObjectAddedEvent,)
from OFS.interfaces import IObjectWillBeAddedEvent

#
# Debug
#
def printEvent(obj, evt):
    print "================"
    print [obj], [evt]
#
# NyFSFile
#
def _handle_obj_version(obj, event_class, *args, **kwargs):
    """ Notify event on obj.version """

    if not 'version' in obj.__dict__.keys():
        return
    version = getattr(obj, 'version', None)
    if not version:
        return
    zope_event.notify(event_class(version, *args, **kwargs))

def _handle_obj_versions(obj, event_class, *args, **kwargs):
    """ Notify event on obj.versions """

    getVersionsContainer = getattr(obj, 'getVersionsContainer', None)
    if not getVersionsContainer:
        return
    versions = getVersionsContainer()
    zope_event.notify(event_class(versions, *args, **kwargs))

def afterAddNyFSFile(obj, event):
    """ Added """

    ext_file = obj.get_data(as_string=False)
    ext_file_id = ext_file.getId()
    if IObjectRemovedEvent.providedBy(event):
        _handle_obj_version(obj, ObjectRemovedEvent, obj)
        _handle_obj_versions(obj, ObjectRemovedEvent, obj)
        return zope_event.notify(ObjectRemovedEvent(ext_file, obj))
    if IObjectAddedEvent.providedBy(event):
        _handle_obj_version(obj, ObjectAddedEvent, obj, 'version')
        _handle_obj_versions(obj, ObjectAddedEvent, obj, 'versions')
        return zope_event.notify(ObjectAddedEvent(ext_file, obj, ext_file_id))
    _handle_obj_version(obj, ObjectMovedEvent, obj, 'version', obj, 'version')
    _handle_obj_versions(obj, ObjectMovedEvent,
                         obj, 'versions', obj, 'versions')
    zope_event.notify(ObjectMovedEvent(
        ext_file, obj, ext_file_id, obj, ext_file_id))

def afterCloneNyFSFile(obj, event):
    """ Copy & Paste"""

    _handle_obj_version(obj, ObjectClonedEvent)
    _handle_obj_versions(obj, ObjectClonedEvent)
    zope_event.notify(ObjectClonedEvent(obj.get_data(as_string=False)))

def beforeDeleteNyFSFile(obj, event):
    """ Delete NyFSFile """

    # Notify object
    ext_file = obj.get_data(as_string=False)
    _handle_obj_version(obj, ObjectWillBeRemovedEvent, obj, 'version')
    _handle_obj_versions(obj, ObjectWillBeRemovedEvent, obj, 'versions')
    zope_event.notify(ObjectWillBeRemovedEvent(ext_file, obj, ext_file.getId()))
#
# NyItem
#
def beforeMoveNyItem(obj, event):
    """A NyItem will be moved."""

    if not IObjectWillBeAddedEvent.providedBy(event):
        obj.uncatalogNyObject(obj)

def modifiedNyItem(obj, event):
    if not IObjectRemovedEvent.providedBy(event):
        #a NyItem was added to a container
        obj.catalogNyObject(obj)
    if not IObjectRemovedEvent.providedBy(event) and \
       not IObjectAddedEvent.providedBy(event):
        #a NyItem was moved.
        obj.catalogNyObject(obj)
#
# NyContainer
#
def beforeMoveNyContainer(obj, event):
    """A NyContainer will be moved."""

    if not IObjectWillBeAddedEvent.providedBy(event):
        obj.uncatalogNyObject(obj)

def modifiedNyContainer(obj, event):
    if not IObjectRemovedEvent.providedBy(event):
        #a NyContainer was added to a container
        obj.catalogNyObject(obj)
    if not IObjectRemovedEvent.providedBy(event) and \
       not IObjectAddedEvent.providedBy(event):
        #a NyContainer was moved.
        obj.catalogNyObject(obj)
