from zope.component.interfaces import ObjectEvent
from zope import interface
from interfaces import IItemTranslationChanged

class ItemTranslationChanged(ObjectEvent):
    interface.implements(IItemTranslationChanged)

    def __init__(self, item, language, value):
        ObjectEvent.__init__(self, item)
        self.language = language
        self.value = value
