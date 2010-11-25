from AccessControl.Permission import Permission

from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.SchemaTool.widgets.Widget import widgetid_from_propname
try:
    from naaya.content.base.discover import get_pluggable_content
except ImportError:
    from Products.NaayaContent.discover import get_pluggable_content

from naaya.content.meeting.meeting import NyMeeting
from naaya.content.meeting import PERMISSION_PARTICIPATE_IN_MEETING
from naaya.content.meeting import (OBSERVER_ROLE, WAITING_ROLE, PARTICIPANT_ROLE,
        ADMINISTRATOR_ROLE, MANAGER_ROLE)
from meeting import add_observer_role

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

