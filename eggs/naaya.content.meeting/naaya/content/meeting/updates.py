import re
from datetime import datetime

from AccessControl.Permission import Permission

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.NaayaCore.SchemaTool.widgets.Widget import widgetid_from_propname
from naaya.core.custom_types import Interval
from naaya.core.zope2util import get_zope_env
try:
    from naaya.content.base.discover import get_pluggable_content
except ImportError:
    from Products.NaayaContent.discover import get_pluggable_content

from naaya.content.meeting.meeting import NyMeeting
from permissions import PERMISSION_PARTICIPATE_IN_MEETING
from naaya.content.meeting import (OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,
        ADMINISTRATOR_ROLE, MANAGER_ROLE)
from meeting import add_observer_role


def interval_from_raw_time(start_date, end_date, raw_time):
    """
    Input: `raw_time` - any string user input that references a time interval
    `start_date`, `end_date` - date string as '%d/%m/%Y'
    Output: Interval object
    """
    all_day = True
    start_time = ''
    end_time = ''

    timepat = re.compile(r'([0-2]?\d([:\.]\d\d?)?)')
    time_pieces = [first for (first, last) in re.findall(timepat, raw_time)]
    ampat = re.compile(r'[^a-z]?(am|pm)[^a-z]?', re.IGNORECASE)
    ampm_pieces = re.findall(ampat, raw_time)
    if len(time_pieces) == 1:
        # Only found start time
        # Creating Interval will raise an Exception that will be handled
        start_time = time_pieces[0].replace('.', ':')
        (end_time, all_day) = ('', False)
    elif len(time_pieces) > 1:
        # set start time to time_pieces[0]
        # set end time to time_pieces[-1]
        start_time = time_pieces[0].replace('.', ':')
        end_time = time_pieces[-1].replace('.', ':')

        # normalize
        if start_time.find(':') == -1:
            start_time += ':00'
        if end_time.find(':') == -1:
            end_time += ':00'

        # PM adjustment
        if len(ampm_pieces):
            (st_h, st_m) = start_time.split(':', 1)
            (en_h, en_m) = end_time.split(':', 1)

            if len(ampm_pieces) == 1:
                # one am/pm specification in the whole string
                # adjust both
                st_ampm = en_ampm = ampm_pieces[0].lower()

            elif len(ampm_pieces) > 1:
                # am/pm for both (or all specified hours)
                st_ampm = ampm_pieces[0].lower()
                en_ampm = ampm_pieces[-1].lower()
            # actual adjustment
            if int(st_h) < 12 and st_ampm == 'pm':
                st_h = str(int(st_h) + 12)
            if int(en_h) < 12 and en_ampm == 'pm':
                en_h = str(int(en_h) + 12)
            # recompose hh:mm
            start_time = st_h + ':' + st_m
            end_time = en_h + ':' + en_m
        all_day = False
    return Interval(start_date, start_time, end_date, end_time, all_day)


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
                start_date = meeting.start_date
                end_date = getattr(meeting, 'end_date', '')
                # old NyMeeting accepted only start_date, interval obj reqs both
                if not end_date:
                    end_date = start_date
                (start_date, end_date) = (start_date.strftime('%d/%m/%Y'),
                                          end_date.strftime('%d/%m/%Y'))

                try:
                    i = interval_from_raw_time(start_date, end_date, time)
                except Exception, e:
                    self.log.error('Can not create Interval: %s' % str(e))
                    try:
                        i = Interval(start_date, '', end_date, '', True)
                    except Exception, e_inner:
                        today = datetime.now().strftime('%d/%m/%Y')
                        i = Interval(today, '', today, '', True)
                        self.log.error('Using TODAY as start/end dates, reason: %s'
                                       % str(e_inner))
                    self.log.error('IMPORTANT: Please manually edit meeting, ' +
                                   ('interval currently set as %s; ' % repr(i))
                                   + ('Old Values: (%s, %s, \'%s\')'
                                    % (start_date, end_date, time)))
                else:
                    self.log.debug(('Successfully converted (%s, %s, \'%s\'), '
                                    % (start_date, end_date, time)) +
                                    'setting meeting.interval: %s' % repr(i))

                meeting.interval = i
                delattr(meeting, 'start_date')
                delattr(meeting, 'end_date')
                delattr(meeting, 'time')
            else:
                self.log.debug('Skipping new-version/patched meeting object at %s' %
                               meeting.absolute_url(1))
        return True

class AddSchemaWidget(UpdateScript):
    title = '"This is an Eionet Meeting" schema widget'
    authors = ('Valentin Dumitru', )
    creation_date = 'Sep 11, 2013'
    description = ('NyMeeting: Add the "This is an Eionet Meeting" '
                    'schema widget, if missing')

    def _update(self, portal):
        meta_type = 'Naaya Meeting'
        NETWORK_NAME = get_zope_env('NETWORK_NAME', '')
        if not portal.is_pluggable_item_installed(meta_type):
            self.log.debug('Meeting not installed')
            return True

        self.log.debug('Changing meeting schema')
        schema_tool = portal.getSchemaTool()
        schema = schema_tool.getSchemaForMetatype(NyMeeting.meta_type)
        crt_widgets = schema.objectIds()
        if widgetid_from_propname('is_eionet_meeting') not in crt_widgets:
            property_schema = get_pluggable_content()[NyMeeting.meta_type]['default_schema']['is_eionet_meeting']
            if NETWORK_NAME.lower() != 'eionet':
                property_schema['visible'] = False
            schema.addWidget('is_eionet_meeting', **property_schema)
            self.log.debug(('Naaya Meeting schema changes: '
                            'added the "Eionet Meeting" widget'))
        else:
            self.log.debug('Meeting schema already contained is_eionet_meeting-property')

        return True

class MakeParticipantsSubscribers(UpdateScript):
    title = 'Participants to subscribers'
    authors = ['Valentin Dumitru']
    creation_date = 'Sep 23, 2013'
    priority = PRIORITY['HIGH']
    description = ('Make all meeting participants subscribers '
            '(if they are not signups)')

    def _update(self, portal):
        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            subscriptions = meeting.getParticipants().getSubscriptions()
            self.log.debug('Found meeting object at %s' % meeting.absolute_url(1))
            for attendee in meeting.getParticipants().getAttendees():
                if not (subscriptions._is_signup(attendee) or
                        subscriptions.getAccountSubscription(attendee)):
                    subscriptions._add_account_subscription(attendee, accept=True)
                    self.log.debug('Added account subscription for user %s'
                                    % attendee)
        return True

class UpdateViewPermission(UpdateScript):
    """ Setting view permission for observer and waiting role  """
    title = 'View permission for observer and waiting roles'
    creation_date = 'Sep 25, 2013'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ('Sets view permission for observer and waiting roles. '
                    'Useful in case of signups')


    def _update(self, portal):
        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            view_perm = Permission('View', (), meeting)
            for role in [OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE]:
                roles = view_perm.getRoles()
                if role not in roles:
                    roles.append(role)
                    view_perm.setRoles(roles)
                    self.log.info("View Permission set for %s on %s" %
                            (role, meeting.absolute_url()))
        return True
