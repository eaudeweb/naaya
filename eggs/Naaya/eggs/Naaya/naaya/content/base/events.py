from zope.interface import implements
from zope.event import notify
from zope.component import adapter
from zope.app.container.interfaces import IObjectMovedEvent

from interfaces import INyContentObject
from interfaces import INyContentObjectAddEvent
from interfaces import INyContentObjectEditEvent
from interfaces import INyContentObjectMovedEvent

class NyContentObjectAddEvent(object):
    """ Naaya content object has been created """
    implements(INyContentObjectAddEvent)

    def __init__(self, context, contributor, schema_data):
        self.context = context
        self.contributor = contributor
        self.schema = schema_data


class NyContentObjectEditEvent(object):
    """ Naaya content object has been edited """
    implements(INyContentObjectEditEvent)

    def __init__(self, context, contributor):
        self.context = context
        self.contributor = contributor

class NyContentObjectMovedEvent(object):
    """ Naaya content object has been moved/renamed """
    implements(INyContentObjectMovedEvent)

    def __init__(self, context, zope_event, old_site_path, new_site_path):
        self.context = context
        self.zope_event = zope_event
        self.old_site_path = old_site_path
        self.new_site_path = new_site_path

@adapter(INyContentObject, IObjectMovedEvent)
def notify_content_object_moved(obj, event):
    if event.oldParent is None or event.newParent is None:
        return # this is actually an added/removed event; skip it...


    new_pp = obj.getPhysicalPath()
    new_parent_pp = event.newParent.getPhysicalPath()
    old_parent_pp = event.oldParent.getPhysicalPath()
    assert new_pp[:len(new_parent_pp)] == new_parent_pp
    assert new_pp[len(new_parent_pp)] == event.newName
    old_pp = (old_parent_pp + (event.oldName,) +
              new_pp[len(new_parent_pp)+1:])

    site = obj.getSite()
    site_pp = site.getPhysicalPath()
    if old_pp[:len(site_pp)] != site_pp:
        # old site path and new site path are different
        # object moved between sites, or the site itself is being moved
        # ignore this event
        return

    old_site_path = '/'.join(old_pp[len(site_pp):])
    new_site_path = '/'.join(new_pp[len(site_pp):])

    notify(NyContentObjectMovedEvent(obj, event, old_site_path, new_site_path))
