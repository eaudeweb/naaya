import os
import sys

from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.utils import get_portal_path
from Products.PythonScripts.PythonScript import manage_addPythonScript

try:
    from Products.RDFCalendar.RDFCalendar import manage_addRDFCalendar, \
                                                RDFCalendar
    rdf_calendar_available = True
except:
    rdf_calendar_available = False

class UpdateRDFCalendar(UpdateScript):
    title = 'Update RDF Calendar'
    description = ('Replaces local RDFSummary objects with Python Script, crea'
                  'te DateIndexes in portal_catalog')
    authors = ['Alexandru Plugaru', ]
    creation_date = 'Jan 01, 2010'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        rdf_calendars = portal.objectValues([RDFCalendar.meta_type, ])
        if rdf_calendar_available and len(rdf_calendars):
            try: #deleteing DateRangeIndex if availalble
                portal.getCatalogTool().delIndex('resource_interval')
                self.log.debug('Deleted resource_interval (DateRangeIndex) fro'
                               'm portal_catalog')
            except:
                pass
            #adding start_end and end_date indexes
            portal.getCatalogTool().addIndex('start_date', 'DateIndex')
            self.log.debug('Added start_date (DateIndex) to portal_catalog')

            portal.getCatalogTool().addIndex('end_date', 'DateIndex')
            self.log.debug('Added end_date (DateIndex) to portal_catalog')

            portal_path = get_portal_path(self, portal)
            script_content = open(portal_path +
                    '/skel/others/local_events.py', 'r').read()
            for rdfcalendar_ob in rdf_calendars:
                try:
                    rdfcalendar_ob.manage_delObjects(['self_events', ])
                    self.log.debug('Removed self_events (RDFSummary) to\
                                   RDFCalendar')
                except:
                    break
                #adding local_events Script (Python) from Naaya skel
                manage_addPythonScript(rdfcalendar_ob, 'local_events')
                local_events_ob = rdfcalendar_ob._getOb('local_events')
                local_events_ob._params = 'year=None, month=None, day=None'
                local_events_ob.write(script_content)
                self.log.debug('Added local_events (Python Script) to RDFCalen'
                               'dar')
        return True
