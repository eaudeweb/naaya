"""
Heartbeat - an event that fires every ~15 minutes, called by a cron script.

Example use::

    from zope import component
    from naaya.core.heartbeat import IHeartbeat
    from Products.Naaya.interfaces import INySite

    @component.adapter(INySite, IHeartbeat)
    def cleanupUnsubmittedObjects(site, hb):
        site.cleanupUnsubmittedObjects(site.get_site_uid())

    component.provideHandler(cleanupUnsubmittedObjects)
"""

from datetime import datetime, timedelta

from zope.interface import implements
from zope.component import adapter

from Products.Naaya.interfaces import INySite
from naaya.core.utils import cooldown
from interfaces import IHeartbeat

class Heartbeat(object):
    implements(IHeartbeat)
    def __init__(self):
        self.when = datetime.now()


@adapter(INySite, IHeartbeat)
def cleanup_unsubmitted_objects(site, hb):
    """
    Clean up unsubmitted objects (documents, stories) older than 1 day.
    """

    name = 'site cleanup unsubmitted %r' % physical_path(site)
    if cooldown(name, timedelta(hours=6)):
        return

    site.cleanupUnsubmittedObjects(site.get_site_uid())

def physical_path(ob):
    return '/'.join(ob.getPhysicalPath())

@adapter(INySite, IHeartbeat)
def rdfcalendar_cron(site, hb):
    """
    Update any RDFCalendar objects in the site's root
    """
    import transaction
    print 'rdfcal update for %r' % physical_path(site)

    name = 'site rdfcalendar %r' % physical_path(site)
    if cooldown(name, timedelta(hours=6)):
        print 'nah'
        return
    print 'go!'

    transaction.commit() # commit earlier stuff; fresh transaction

    try:
        for rdfcal in site.objectValues(['RDF Calendar']):
            rdfcal.manage_updateChannels()
    except:
        site.log_current_error()
        transaction.abort()
    else:
        transaction.get().note("RDFCalendar cron %r" % physical_path(site))
        transaction.commit()
