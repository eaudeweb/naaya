from AccessControl.Permission import Permission

from Products.naayaUpdater.updates import UpdateScript

from meeting import _restrict_meeting_item_view, _restrict_meeting_agenda_view
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

class RestrictObjectsInMeetings(UpdateScript):
    title = 'Restrict objects in current existing meetings'
    authors = ['Andrei Laza']
    creation_date = 'Sep 09, 2010'

    def _update(self, portal):
        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            self.log.debug('Found meeting object at %s' % meeting.absolute_url(1))
            items = meeting.objectValues()
            for item in items:
                _restrict_meeting_item_view(item)
                self.log.debug('Restricted permissions for item %s' %
                        item.absolute_url(1))

            agenda_pointer = getattr(meeting, 'agenda_pointer', '')
            if agenda_pointer:
                try:
                    agenda = portal.unrestrictedTraverse(str(agenda_pointer))
                except KeyError:
                    agenda = None
                if agenda is not None:
                    self.log.debug('Restricted permissions for agenda %s' %
                            agenda.absolute_url(1))
                    _restrict_meeting_agenda_view(agenda)
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

