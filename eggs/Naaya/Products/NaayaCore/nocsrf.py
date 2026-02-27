"""No-op replacement for plone.protect CSRF transform (not needed for Naaya)"""

from plone.transformchain.interfaces import ITransform
from zope.interface import implementer, Interface
from zope.component import adapter


@implementer(ITransform)
@adapter(Interface, Interface)
class NoOpTransform:
    order = 9000

    def __init__(self, published, request):
        pass

    def transformUnicode(self, result, encoding):
        return None

    def transformBytes(self, result, encoding):
        return None

    def transformIterable(self, result, encoding):
        return None
