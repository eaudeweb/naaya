from zope.interface import implements
from interfaces import INyPluggableItemInstalled, ISkelLoad

class NyPluggableItemInstalled(object):
    implements(INyPluggableItemInstalled)

    def __init__(self, context, meta_type):
        self.context = context
        self.meta_type = meta_type


class SkelLoad(object):
    implements(ISkelLoad)

    def __init__(self, site, skel_handler):
        self.site = site
        self.skel_handler = skel_handler
