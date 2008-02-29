# Python imports
import sys
import time

# Zope imports
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from zLOG import LOG, DEBUG, INFO, ERROR

# Naaya imports
from Products.Naaya.constants import METATYPE_NYSITE

from constants import CATALOG_ID


PERMISSION_ADD_CRON_TOOL = 'Naaya - Add Naaya Cron Tool'
PERMISSION_USE_CRON_TOOL = 'Naaya - Use Naaya Cron Tool'

CRON_TOOL_ID = 'cron_tool'

def manage_addCronTool(context, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    ob = CronTool(CRON_TOOL_ID, title='Naaya Cron Tool', jobs=[])
    context._setObject(CRON_TOOL_ID, ob)

    if REQUEST:
        return context.manage_main(context, REQUEST, update_menu=1)
    return id

class CronTool(Folder):
    """Naaya Cron Tool"""

    meta_type = 'Naaya Cron Tool'
    _constructors = (manage_addCronTool,)
    security = ClassSecurityInfo()

    manage_options= Folder.manage_options + ()

    _properties=(
        {'id':'title', 'type':'string', 'mode':'w', 'label':'Title'},
        {'id':'jobs', 'type':'lines', 'mode':'w', 'label':'Jobs'},
    )

    def __init__(self, id, **kw):
        Folder.__init__(self, id)
        self.manage_changeProperties(**kw)
        self.last_time = {}

    security.declarePrivate('getSites')
    def getSites(self):
        """ """
        root = self.restrictedTraverse('/')
        catalog = root._getOb(CATALOG_ID)
        sites = [brain.getObject() for brain in catalog({'meta_type': ['Naaya Site']})]
        return sites

    security.declareProtected(PERMISSION_USE_CRON_TOOL, 'runJobs')
    def runJobs(self, REQUEST=None):
        """ """
        errors = []
        for line in self.jobs:
            try:
                interval, job = line.split(' ', 1)
                interval = int(interval) * 60 # minutes -> seconds
            except ValueError:
                err = sys.exc_info()
                errors.append(err)
                LOG('Naaya Admin Tool', ERROR,
                    'Error parsing line "%s"' % (line, ) , error=err)
                continue

            now = time.time()
            last_time = self.last_time.get(job, 0)
            if now - last_time < interval:
                # the first time or too early
                LOG('Naaya Admin Tool', DEBUG,
                    '''It's too early to run job "%s"''' % (job, ))
                continue

            for site in self.getSites():
                LOG('Naaya Admin Tool', INFO,
                    'Running "%s" for site "%s"' % (job, site.absolute_url()))
                try:
                    exec job in {}, {'site': site}
                    LOG('Naaya Admin Tool', INFO,
                         'Finished running "%s" for site "%s"' % (job, site.absolute_url()))
                except:
                    err = sys.exc_info()
                    errors.append(err)
                    LOG('Naaya Admin Tool', ERROR,
                         'Error running line "%s" for site "%s"' % (line, site.absolute_url()), error=err)

            self.last_time[job] = now
            self._p_changed = 1

        if errors:
            return 'ERROR'
        return 'OK'

    security.declareProtected(PERMISSION_USE_CRON_TOOL, 'resetTimers')
    def resetTimers(self):
        """ """
        LOG('Naaya Admin Tool', INFO, 'Timers reset')
        self.last_time.clear()
        self._p_changed = 1

InitializeClass(CronTool)
