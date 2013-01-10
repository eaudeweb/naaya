import time
from datetime import datetime
import operator

from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from naaya.core.utils import pretty_size
from Products.Naaya.interfaces import INySite


def blobstorage_stats(app):
    stats = {}
    for ob in app.objectValues():
        if INySite.providedBy(ob):
            s_id = ob.getId()
            stats[s_id] = {'du': 0, 'objects': 0, 'versions': 0, 'extra': {}}
            catalog = ob.getCatalogTool()
            bfile_brains = catalog({'meta_type': ['Naaya Blob File',
                                                  'Naaya Localized Blob File']})
            for brain in bfile_brains:
                try:
                    bfile = brain.getObject()
                except Exception, e:
                    continue # bad brain?
                else:
                    stats[s_id]['objects'] += 1
                    if bfile.meta_type == 'Naaya Localized Blob File':
                        sizes = 0
                        for lg in bfile._versions.values():
                            stats[s_id]['versions'] += len(lg)
                            sizes = reduce(operator.add,
                                           [v.size or 0 for v in lg], sizes)
                    else:
                        stats[s_id]['versions'] += len(bfile._versions)
                        sizes = [v.size or 0 for v in bfile._versions]
                    stats[s_id]['du'] = reduce(operator.add, sizes,
                                               stats[s_id]['du'])
    return (stats, time.time())


def manage_addStatsItem(self, REQUEST=None, RESPONSE=None):
    """ Add a Naaya Monitor Blobusage Stats instance """
    stats = blobstorage_stats(self.unrestrictedTraverse("/"))
    dt = datetime.fromtimestamp(stats[1])
    ob_id = dt.strftime("%Y_%m_%d_%H_%M")
    self._setObject(ob_id, StatsItem(ob_id, ob_id, stats))
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('manage_main')

class StatsItem(SimpleItem):

    meta_type = 'Naaya Monitor Blobusage Stats'
    icon = '++resource++naaya_monitor/stats_item.png'
    security = ClassSecurityInfo()

    def __init__(self, id, title, stats):
        self.stats = stats
        super(StatsItem, self).__init__(id, title)

    security.declareProtected(view_management_screens, 'manage_workspace')
    def manage_workspace(self, REQUEST, RESPONSE):
        """ """
        pt = PageTemplateFile('zpt/stats_item', globals())
        dt = datetime.fromtimestamp(self.stats[1])
        formatted_stats = []
        for site_id, values in self.stats[0].items():
            formatted_stats.append(values)
            entry = formatted_stats[-1]
            entry['pretty_size'] = pretty_size(entry['du'])
            ob = self.unrestrictedTraverse("/").get(site_id, None)
            if ob:
                entry.update(site_url=ob.absolute_url(),
                             site_title=ob.title_or_id())
            else:
                entry.update(site_url='#', site_title='%s (removed)' % site_id)
        formatted_stats.sort(key=lambda x: x['du'], reverse=True)
        return pt.__of__(self)(stats=formatted_stats,
                               date=dt.strftime("%Y-%m-%d %H:%M"))
