#Python imports
import re

#Zope imports
from AccessControl import ClassSecurityInfo

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import physical_path
from update_add_portlets_onerror_to_standard_template import get_standard_template

class UpdateAddStandardHeadLinksMacro(UpdateScript):
    """ Add standard head links macro """
    title = ' Add standard head links macro '
    creation_date = 'Dec 9, 2010'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ' Add standard head links macro '
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s: <a href="%(url)s/manage_main">current skin standard template</a>'

        self.log.debug(physical_path(portal))
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        macro_start = '<metal:block define-macro="standard-head-links">'
        macro_end = '</metal:block>'
        slot_start = '<metal:block define-slot="standard-head-links">'
        slot_end = '</metal:block>'

        if re.search(slot_start, tal) is None:
            self.log.info(t % {'info': "can't find slot",
                               'url': standard_template.absolute_url()})
            return True

        if re.search(macro_start, tal) is not None:
            return True

        pattern = '(\s*)%s((?:.|\n)*?)%s' % (slot_start, slot_end)
        replacement = '\\1%s\\1%s\\2%s\\1%s' % (slot_start, macro_start, macro_end, slot_end)
        tal = re.sub(pattern, replacement, tal)
        self.log.info(t % {'info': 'added macro',
                           'url': standard_template.absolute_url()})
        standard_template.write(tal)
        return True

