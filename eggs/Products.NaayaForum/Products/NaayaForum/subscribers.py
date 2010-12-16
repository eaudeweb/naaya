from interfaces import INyForumObjectAddEvent, INyForumObjectEditEvent
from OFS.interfaces import IObjectWillBeAddedEvent

def handle_forum_object_add(event):
    obj = event.context
    contributor = event.contributor
    notification_tool = obj.getSite().getNotificationTool()
    notification_tool.notify_instant(obj, contributor)

def handle_forum_object_edit(event):
    obj = event.context
    contributor = event.contributor
    notification_tool = obj.getSite().getNotificationTool()
    notification_tool.notify_instant(obj, contributor, ob_edited=True)

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
