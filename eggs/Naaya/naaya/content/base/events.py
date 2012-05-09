from DateTime import DateTime
from zope.interface import implements
from zope.event import notify
from zope.component import adapter
from zope.app.container.interfaces import IObjectMovedEvent

from interfaces import INyContentObject
from interfaces import INyContentObjectAddEvent
from interfaces import INyContentObjectEditEvent
from interfaces import INyContentObjectApproveEvent
from interfaces import INyContentObjectUnapproveEvent
from interfaces import INyContentObjectMovedEvent
from interfaces import INyContentObjectOpenEvent
from interfaces import INyContentObjectDownloadEvent

from naaya.core.zope2util import get_or_create_site_logger

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

class NyContentObjectApproveEvent(object):
    """ Naaya content object has been approved """
    implements(INyContentObjectApproveEvent)

    def __init__(self, context, contributor, **kw):
        self.__dict__.update(kw)
        self.context = context
        self.contributor = contributor

class NyContentObjectUnapproveEvent(object):
    """ Naaya content object has been unapproved """
    implements(INyContentObjectUnapproveEvent)

    def __init__(self, context, contributor, **kw):
        self.__dict__.update(kw)
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

class NyContentObjectOpenEvent(object):
    """ Naaya content object has been opened """
    implements(INyContentObjectOpenEvent)

    def __init__(self, context):
        self.context = context

class NyContentObjectDownloadEvent(object):
    """ Naaya content object has been downloaded """
    implements(INyContentObjectDownloadEvent)

    def __init__(self, context):
        self.context = context

@adapter(INyContentObject, IObjectMovedEvent)
def notify_content_object_moved(obj, event):
    if event.oldParent is None or event.newParent is None:
        return # this is actually an added/removed event; skip it...

    if hasattr(obj, 'submitted') and obj.submitted == 0: #Not submited, skip
        return

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

def update_last_modification(event):
    obj = event.context
    if not hasattr(obj, 'version') or not obj.version:
        obj.last_modification = DateTime()

def log_open_event(event):
    """ Log open action on object """
    context = event.context
    site_id = context.getSite().id
    user = context.REQUEST.AUTHENTICATED_USER.getUserName()

    logger = get_or_create_site_logger(site_id)
    message = "%s on %s (%s) by %s" % ('OPEN', context.title_or_id(),
                                       context.meta_type, user)
    logger.info(message)

def log_download_event(event):
    """ Log download action on object """
    context = event.context
    site_id = context.getSite().id
    user = context.REQUEST.AUTHENTICATED_USER.getUserName()

    logger = get_or_create_site_logger(site_id)
    message = "%s on %s (%s) by %s" % ('DOWNLOAD', context.title_or_id(),
                                       context.meta_type, user)
    logger.info(message)
