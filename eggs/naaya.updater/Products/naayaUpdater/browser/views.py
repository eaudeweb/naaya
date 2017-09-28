from time import strptime
import operator
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
        ret = []
        for product, scripts in self.categories.items():
            for script in scripts:
                ret.append((script, product))

        def sort_date(item):
            try:
                return strptime(item[0].creation_date, '%b %d, %Y')
            except ValueError:
                return None
        ret.sort(key=sort_date, reverse=True)
        return ret



class LogsView(BrowserView):
    """ Display logs """

    @property
    def logs(self):
        return sorted(self.context._logs,
                      key=operator.itemgetter(1),
                      reverse=True)
