#Python imports
import re

#Zope imports
from AccessControl import ClassSecurityInfo

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from utils import pat, physical_path, get_standard_template

class UpdateAddOnerrorForStandardTemplateBreadcrumb(UpdateScript):
    """ Add on error for standard template breadcrumb """
    title = ' Add on error for standard template breadcrumb '
    creation_date = 'Mar 8, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = ' Add on error for standard template breadcrumb '
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        t = '%(info)s: <a href="%(url)s/manage_main">current skin standard template</a>'

        self.log.debug(physical_path(portal))
        standard_template = get_standard_template(portal)
        tal = standard_template.read()

        str_no_error = '<div id="breadcrumbtrail" '
        str_with_error_old = '<div id="breadcrumbtrail" on-error="here/rstk/catch_unauthorized" '
        str_with_error = '<div id="breadcrumbtrail" on-error="python:here.log_page_error(error)" '

        if str_with_error in tal:
            self.log.debug('"on-error" for breadcrumb already in standard template')
            return True

        if str_no_error not in tal:
            self.log.debug('could not find breadcrumb in standard template')
            return False

        if str_with_error_old in tal:
            tal = tal.replace(str_with_error_old, str_with_error)
        else:
            tal = tal.replace(str_no_error, str_with_error)
        standard_template.write(tal)

        self.log.debug('Added "on-error" for breadcrumb in standard template')
        return True
