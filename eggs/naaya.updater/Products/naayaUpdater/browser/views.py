from time import strptime
from datetime import date
import operator
from zope.component import getUtility
from zope.component import getUtilitiesFor
from Products.Five.browser import BrowserView

from Products.naayaUpdater.interfaces import IUpdateScript

class UpdateScriptsView(BrowserView):
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
        def sort_date(script):
            try:
                t = strptime(script.creation_date, '%b %d, %Y')
                return date(t.tm_year, t.tm_mon, t.tm_mday)
            except ValueError:
                return date(2000, 1, 1)

        for category, scripts in items:
            scripts.sort(key=sort_date, reverse=True)
            scripts.sort(key=operator.attrgetter('priority'))
            yield category, scripts

class LogsView(BrowserView):
    """ Display logs """

    @property
    def logs(self):
        return sorted(self.context._logs,
                      key=operator.itemgetter(1),
                      reverse=True)
