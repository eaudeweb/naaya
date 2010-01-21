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

    def __init__(self, obj, event):
        new_pp = obj.getPhysicalPath()
        new_parent_pp = event.newParent.getPhysicalPath()
        old_parent_pp = event.oldParent.getPhysicalPath()
        assert new_pp[:len(new_parent_pp)] == new_parent_pp
        assert new_pp[len(new_parent_pp)] == event.newName
        old_pp = (old_parent_pp + (event.oldName,) +
                  new_pp[len(new_parent_pp)+1:])

        site = obj.getSite()
        site_pp = site.getPhysicalPath()
        assert old_pp[:len(site_pp)] == site_pp

        self.old_site_path = '/'.join(old_pp[len(site_pp):])
        self.new_site_path = '/'.join(new_pp[len(site_pp):])
        self.context = obj
        self.zope_event = event

@adapter(INyContentObject, IObjectMovedEvent)
def notify_content_object_moved(obj, event):
    if event.oldParent is None or event.newParent is None:
        return # this is actually an added/removed event; skip it...

    notify(NyContentObjectMovedEvent(obj, event))
