from Products.naayaUpdater.updates import UpdateScript

class AddAllowRegister(UpdateScript):
    title = 'Add allow register attribute for the meetings'
    authors = ['Andrei Laza']
    creation_date = 'Sep 08, 2010'

    def _update(self, portal):
        meetings = portal.getCatalogedObjects(meta_type='Naaya Meeting')
        for meeting in meetings:
            if not hasattr(meeting, 'allow_register'):
                meeting.allow_register = True
                self.log.debug('Added allow_register attribute for meeting at ',
                        meeting.absolute_url(1))
        return True
