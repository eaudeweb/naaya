from Acquisition import aq_base
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.deferredimport import deprecated
from zope.deprecation.deprecation import DeprecatedMethod
from contentratings.interfaces import IObjectRatedEvent
from contentratings.interfaces import IObjectUserRatedEvent
from contentratings.interfaces import IObjectEditorRatedEvent

@implementer(IObjectRatedEvent)
class ObjectRatedEvent(ObjectModifiedEvent):
    """An event that will be used to trigger necessary actions on rating
       changes"""
    def __init__(self, object, rating, category=''):
        self.rating = rating
        self.category = category
        super(ObjectRatedEvent, self).__init__(object)

def reindexOnRate(obj, event):
    """This belongs in a plone specific package, though for now it
    breaks nothing to keep it here"""
    if getattr(aq_base(obj), 'reindexObject', None) is not None:
        obj.reindexObject()


# BBB: Everything below here is for backwards compat only
@implementer(IObjectUserRatedEvent)
class ObjectUserRatedEvent(ObjectRatedEvent):
    """This exists for BBB only"""

@implementer(IObjectEditorRatedEvent)
class ObjectEditorRatedEvent(ObjectRatedEvent):
    """This exists for BBB only"""

deprecated('The rating type specific events have been deprecated '
           'because they are of limited utility.  Use the generic rating '
           'event, or fire your own events from custom storage or manager.',
           ObjectUserRatedEvent=ObjectUserRatedEvent,
           ObjectEditorRatedEvent=ObjectEditorRatedEvent)


reindexOnEditorRate = DeprecatedMethod(reindexOnRate,
                                       'reindexOnEditorRate is no longer '
                                       'supported, use reindexOnRate')
