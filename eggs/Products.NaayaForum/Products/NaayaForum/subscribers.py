from OFS.interfaces import IObjectWillBeAddedEvent
from interfaces import INyForumObjectAddEvent, INyForumObjectEditEvent

from naaya.core.zope2util import path_in_site
from Products.NaayaCore.NotificationTool.constants import LOG_TYPES

def handle_forum_object_add(event):
    obj = event.context
    portal = obj.getSite()
    contributor = event.contributor
    notification_tool = portal.getNotificationTool()
    notification_tool.notify_instant(obj, contributor)

    if obj.approved: #Create log entry
        action_logger = portal.getActionLogger()
        action_logger.create(type=LOG_TYPES['created'],
                             contributor=contributor, path=path_in_site(obj))

def handle_forum_object_edit(event):
    obj = event.context
    portal = obj.getSite()
    contributor = event.contributor
    notification_tool = portal.getNotificationTool()
    notification_tool.notify_instant(obj, contributor, ob_edited=True)

    if obj.approved: #Create log entry
        action_logger = portal.getActionLogger()
        action_logger.create(type=LOG_TYPES['modified'],
                             contributor=contributor, path=path_in_site(obj))

def handle_forum_deletion(ob, event):
    """The Forum will be moved/removed"""
    if not IObjectWillBeAddedEvent.providedBy(event):
        # Object will be removed:

        #Statistics db should  not be removed.
        #If forum is undeleted then the statistics should still be there.
        #ob._removeStatisticsContainer()
        pass

def handle_topic_deletion(ob, event):
    """The ForumTopic will be moved/removed"""
    if not IObjectWillBeAddedEvent.providedBy(event):
        # Object will be removed:
        # Same as above. If the topic is deleted by mistake the statistics
        #should still be there in case of undo.
        #ob.aq_inner.aq_parent.removeTopicHits(ob.id)
        pass
