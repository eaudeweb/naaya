from AccessControl import ClassSecurityInfo
from zope.component import queryAdapter
from AccessControl.Permissions import view_management_screens
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.managers.utils import html_diff

from Products.naayaUpdater.updates import UpdateScript, PRIORITY


class UpdatePortletAdministration(UpdateScript):
    """ Update portlet administration """
    title = 'Compare & Migrate portlet administration back to disk'
    creation_date = 'Oct 13, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']
    description = 'This is related to the admin top content page'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        portlet_name = 'portlet_administration'
        ptool = portal.portal_portlets

        site_portlet = queryAdapter(portal, INyPortlet, name=portlet_name)
        assert site_portlet is not None
        self.log.debug(site_portlet)

        custom_portlet = ptool._getOb(portlet_name, None)
        if custom_portlet is None:
            self.log.debug('No local portlet_administration')
            return True

        revert_url = portal.absolute_url() + '/portal_portlets/manage_main'
        revert_link = '<a href="%s">portal_portlets</a>' % revert_url
        diff = html_diff(site_portlet.template._text, custom_portlet._text)

        self.report_html = '<br/>'.join([revert_link, diff])
        return True

    security.declareProtected(view_management_screens, 'standard_update_template')
    standard_update_template = PageTemplateFile('zpt/update_template', globals())

    security.declareProtected(view_management_screens, 'update_template')
    update_template = PageTemplateFile('zpt/update_portlet_administration', globals())
