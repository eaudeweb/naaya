import re

from AccessControl.Permission import Permission

from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.SchemaTool.widgets.Widget import widgetid_from_propname
from naaya.core.custom_types import Interval
try:
    from naaya.content.base.discover import get_pluggable_content
except ImportError:
    from Products.NaayaContent.discover import get_pluggable_content

from naaya.content.meeting.meeting import NyMeeting
from naaya.content.meeting import PERMISSION_PARTICIPATE_IN_MEETING
from naaya.content.meeting import (OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,
        ADMINISTRATOR_ROLE, MANAGER_ROLE)
from meeting import add_observer_role


class AddAutoRegister(UpdateScript):
    title = 'Add auto register attribute for the meetings'
    authors = ['Andrei Laza']
    creation_date = 'Mar 08, 2011'

    def _update(self, portal):
        self.log.debug('Changing meeting schema')
        schema_tool = portal.getSchemaTool()
        schema = schema_tool.getSchemaForMetatype(NyMeeting.meta_type)

        try:
            schema.getWidget('auto_register')
        except KeyError:
            pass
        else:
            schema.manage_delObjects([widgetid_from_propname('auto_register')])

        property_schema = get_pluggable_content()[NyMeeting.meta_type]['default_schema']['auto_register']
        schema.addWidget('auto_register', **property_schema)

        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            self.log.debug('Found meeting object at %s' % meeting.absolute_url(1))
            if not hasattr(meeting, 'auto_register'):
                meeting.auto_register = False
                self.log.debug('Added auto_register attribute for meeting at %s' %
                        meeting.absolute_url(1))
        return True


class AddAllowRegister(UpdateScript):
    title = 'Add allow register attribute for the meetings'
    authors = ['Andrei Laza']
    creation_date = 'Sep 08, 2010'

    def _update(self, portal):
        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            self.log.debug('Found meeting object at %s' % meeting.absolute_url(1))
            if not hasattr(meeting, 'allow_register'):
                meeting.allow_register = True
                self.log.debug('Added allow_register attribute for meeting at %s' %
                        meeting.absolute_url(1))
        return True

class AddRestrictItems(UpdateScript):
    title = 'Add restrict_items attribute for the meetings'
    authors = ['Andrei Laza']
    creation_date = 'Nov 25, 2010'

    def _update(self, portal):
        self.log.debug('Changing meeting schema')
        schema_tool = portal.getSchemaTool()
        schema = schema_tool.getSchemaForMetatype(NyMeeting.meta_type)

        try:
            schema.getWidget('restrict_items')
        except KeyError:
            pass
        else:
            schema.manage_delObjects([widgetid_from_propname('restrict_items')])

        property_schema = get_pluggable_content()[NyMeeting.meta_type]['default_schema']['restrict_items']
        schema.addWidget('restrict_items', **property_schema)

        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            self.log.debug('Found meeting object at %s' % meeting.absolute_url(1))
            if not hasattr(meeting, 'restrict_items'):
                meeting.restrict_items = True
                self.log.debug('Added restrict_items attribute for meeting at %s' %
                        meeting.absolute_url(1))
        return True

class RestrictObjectsInMeetings(UpdateScript):
    title = 'Restrict objects in current existing meetings'
    authors = ['Andrei Laza']
    creation_date = 'Sep 09, 2010'

    def _update(self, portal):
        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            self.log.debug('Found meeting object at %s' % meeting.absolute_url(1))
            meeting._set_items_view_permissions()
        return True

class AddObserversInMeetings(UpdateScript):
    title = 'Add observer role in existing meetings (also run restrict objects in meetings)'
    authors = ['Andrei Laza']
    creation_date = 'Oct 30, 2010'

    def _update(self, portal):
        meta_type = 'Naaya Meeting'
        if not portal.is_pluggable_item_installed(meta_type):
            self.log.debug('Meeting not installed')
            return True

        self.log.debug('Adding Observer role')
        add_observer_role(portal)

        self.log.debug('Patching meeting objects')
        meetings = portal.getCatalogedObjects(meta_type)
        for meeting in meetings:
            self.log.debug('Patching meeting object at %s' % meeting.absolute_url(1))
            permission = Permission(PERMISSION_PARTICIPATE_IN_MEETING, (), meeting)
            permission.setRoles([OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE])
        return True

class ConvertMeetingDates(UpdateScript):
    title = 'NyMeeting: Convert the start_date, end_date, "time" string to Interval'
    authors = ('Mihnea Simian', )
    creation_date = 'Mar 29, 2011'

    def _update(self, portal):
        meta_type = 'Naaya Meeting'
        if not portal.is_pluggable_item_installed(meta_type):
            self.log.debug('Meeting not installed')
            return True

        self.log.debug('Changing meeting schema')
        schema_tool = portal.getSchemaTool()
        schema = schema_tool.getSchemaForMetatype(NyMeeting.meta_type)
        crt_widgets = schema.objectIds()
        if widgetid_from_propname('interval') not in crt_widgets:
            schema.manage_delObjects([widgetid_from_propname('start_date'),
                                      widgetid_from_propname('end_date'),
                                      widgetid_from_propname('time')])
            property_schema = get_pluggable_content()[NyMeeting.meta_type]['default_schema']['interval']
            schema.addWidget('interval', **property_schema)
            self.log.debug(('Naaya Meeting schema changes: '
                            '-start_date -end_date -time +interval'))
        else:
            self.log.debug('Meeting schema already contained interval-property')

        self.log.debug('Patching meeting objects')
        meetings = portal.getCatalogedObjects(meta_type)
        for meeting in meetings:
            if getattr(meeting, 'interval', None) is None:
                self.log.debug('Patching meeting object at %s' %
                               meeting.absolute_url(1))
                time = getattr(meeting, 'time', '')
                try:
                    start_date = meeting.start_date.strftime("%d/%m/%Y")
                    end_date = meeting.end_date.strftime("%d/%m/%Y")
                except Exception:
                    self.log.debug('Can not get start/end dates, patch aborted')
                    continue
                self.log.debug('(Start, end date, time) is: (%s, %s, \'%s\')'
                               % (start_date, end_date, time))
                all_day = True
                start_time = ''
                end_time = ''

                timepat = re.compile(r'[0-2]?\d[:\.]\d\d?')
                time_pieces = re.findall(timepat, time)
                if len(time_pieces) == 1:
                    self.log.debug('Only found start_time: \'%s\', drop it'
                                   % time_pieces[0])
                elif len(time_pieces) > 1:
                    # set start time to time_pieces[0]
                    # set end time to time_pieces[-1]
                    start_time = time_pieces[0].replace('.', ':')
                    end_time = time_pieces[-1].replace('.', ':')
                    all_day = False

                i = Interval(start_date, start_time, end_date, end_time, all_day)
                self.log.debug('Setting meeting.interval: %s' % repr(i))
                meeting.interval = i
                delattr(meeting, 'start_date')
                delattr(meeting, 'end_date')
                delattr(meeting, 'time')
            else:
                self.log.debug('Skipping new-version/patched meeting object at %s' %
                               meeting.absolute_url(1))
        return True
