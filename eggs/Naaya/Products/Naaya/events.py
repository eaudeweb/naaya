from zope.interface import implements
from interfaces import INyPluggableItemInstalled

class NyPluggableItemInstalled(object):
    implements(INyPluggableItemInstalled)

    def __init__(self, context, meta_type):
        self.context = context
        self.meta_type = meta_type
