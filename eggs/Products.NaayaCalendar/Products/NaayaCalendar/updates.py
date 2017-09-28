from copy import deepcopy
from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCalendar.EventCalendar import EventCalendar

class UpdateCalendar(UpdateScript):
    title = 'Migration script for NaayaCalendar'
    authors = ['Cornel Nitu']
    description = 'Solve AttributeError: getStyleEventProperty'
    creation_date = 'Oct 21, 2010'

    def _update(self, portal):
        calendar = getattr(portal, 'portal_calendar', None)
        if calendar:
            if calendar.meta_type == 'Naaya Calendar':
                if 'calendar_style' in calendar.objectIds():
                    migrate_calendar(portal, calendar)
                    self.log.info('Update - %s' % physical_path(calendar))
                else:
                    self.log.info('Already updated - %s' % physical_path(calendar))
            else:
                self.log.info('Different meta_type - %s' % physical_path(calendar))
        else:
            self.log.info('Not found - %s' % physical_path(portal))
        return True

def migrate_calendar(portal, calendar):
    ob = EventCalendar(id = calendar.id, 
                        title = calendar.title, 
                        description = calendar.description, 
                        day_len = calendar.day_len, 
                        start_day = calendar.start_day, 
                        catalog = calendar.catalog)
    ob.cal_meta_types = deepcopy(calendar.cal_meta_types)
    portal.manage_delObjects([calendar.id])
    portal._setObject(ob.id, ob)

def physical_path(ob):
    return '/'.join(ob.getPhysicalPath())
