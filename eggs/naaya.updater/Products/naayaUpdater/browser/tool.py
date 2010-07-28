import operator
from zope.component import getUtility
from zope.component import getUtilitiesFor
from Products.Five.browser import BrowserView

from Products.naayaUpdater.interfaces import IUpdateScript

class View(BrowserView):
    """ Tool view
    """
    _categories = {}

    @property
    def categories(self):
        if self._categories:
            return self._categories

        for name, klass in getUtilitiesFor(IUpdateScript):
            utility = klass()
            utility.id = name
            category = '.'.join(utility.__module__.split('.')[:2])
            self._categories.setdefault(category, [])
            self._categories[category].append(utility)
        return self._categories

    @property
    def table(self):
        items = self.categories.items()
        items.sort()
        for category, scripts in items:
            scripts.sort(key=operator.attrgetter('priority'))
            yield category, scripts
