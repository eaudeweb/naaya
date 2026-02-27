from zope.interface import implementer
from .interfaces import INyPluggableItemInstalled, ISkelLoad

@implementer(INyPluggableItemInstalled)
class NyPluggableItemInstalled(object):

    def __init__(self, context, meta_type):
        self.context = context
        self.meta_type = meta_type


@implementer(ISkelLoad)
class SkelLoad(object):

    def __init__(self, site, skel_handler):
        self.site = site
        self.skel_handler = skel_handler
