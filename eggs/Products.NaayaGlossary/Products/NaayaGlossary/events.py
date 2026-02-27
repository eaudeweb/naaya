from zope.interface.interfaces import ObjectEvent
from zope.interface import implementer
from .interfaces import IItemTranslationChanged

@implementer(IItemTranslationChanged)
class ItemTranslationChanged(ObjectEvent):

    def __init__(self, item, language, value):
        ObjectEvent.__init__(self, item)
        self.language = language
        self.value = value
