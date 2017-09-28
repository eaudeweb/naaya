import re

from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.naayaUpdater.updates.utils import get_standard_template

class UpdateHelpdeskCleanup(UpdateScript):
    """ """
    title = 'Cleanup helpdesk references from standard template'
    creation_date = 'Oct 21, 2011'
    authors = ['Valentin Dumitru']
    priority = PRIORITY['LOW']
    description = ('Change feedback link to /feedback_html and remove references to helpdesk from standard_template')

    def _update(self, portal):
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        if 'HelpDesk/" accesskey="9" i18n:translate="">Feedback and helpdesk' not in tal:
            if 'Helpdesk' in tal:
                self.log.error("Helpdesk present in standard_template, but the code is not what we expect it to be...")
            else:
                self.log.debug('Link to helpdesk not in standard_template')
        else:
            tal = tal.replace('HelpDesk/" accesskey="9" i18n:translate="">Feedback and helpdesk', 'feedback_html" accesskey="9" i18n:translate="">Feedback', 1)
            self.log.debug('Helpdesk link removed')
            standard_template.write(tal)

        helpdesks = [ob.getId() for ob in portal.objectValues('Naaya HelpDesk')]
        if len(helpdesks) > 0:
            self.log.debug('Helpdesk objects %s removed' % helpdesks)
            portal.manage_delObjects(helpdesks)
        else:
            self.log.debug('No Naaya HelpDesk object in the portal root')
        return True
