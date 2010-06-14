import os
import sys

from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.update_scripts import UpdateScript
from Products.PythonScripts.PythonScript import manage_addPythonScript

try:
    from Products.RDFCalendar.RDFCalendar import manage_addRDFCalendar, \
                                                RDFCalendar
    rdf_calendar_available = True
except:
    rdf_calendar_available = False

class UpdateRDFCalendar(UpdateScript):
    id = 'update_rdf_calendar'
    title = 'Update RDF Calendar'
    description = 'Replaces local RDFSummary objects with Python Script, creat\
                  e DateRangeIndex in portal_catalog'
    authors = ['Alexandru Plugaru', ]
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        rdf_calendars = portal.objectValues([RDFCalendar.meta_type, ])
        if rdf_calendar_available and len(rdf_calendars):
            #adding range index to catalog
            class Empty(object):
                pass
            extra = Empty() #Extra has to be an object.. see DateRangeIndex
            extra.since_field = 'start_date'
            extra.until_field = 'end_date'
            portal.getCatalogTool().addIndex('resource_interval',
                                             'DateRangeIndex', extra=extra)
            self.log.debug('Added resource_interval (DateRangeIndex) to portal_catalog')
            portal_path = self.get_portal_path(portal)
            script_content = open(portal_path +
                    '/skel/others/local_events.py', 'r').read()
            for rdfcalendar_ob in rdf_calendars:
                try:
                    rdfcalendar_ob.manage_delObjects(['self_events', ])
                    self.log.debug('Removed self_events (RDFSummary) to RDFCalendar')
                except:
                    break
                #adding local_events Script (Python) from Naaya skel
                manage_addPythonScript(rdfcalendar_ob, 'local_events')
                local_events_ob = rdfcalendar_ob._getOb('local_events')
                local_events_ob.write(script_content)
                self.log.debug('Added local_events (Python Script) to RDFCalendar')
        return True

