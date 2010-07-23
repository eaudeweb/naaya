from zope.component import getUtilitiesFor
from Products.Five.browser import BrowserView

from Products.naayaUpdater.interfaces import IUpdateScript

class View(BrowserView):
    """ Tool view
    """
    @property
    def scripts(self):
        for name, klass in getUtilitiesFor(IUpdateScript):
            yield name, klass
