from Products.naayaUpdater.updates import UpdateScript

class UpdateWebEx(UpdateScript):
    """ """
    title = 'Adding the WebEx planning email functionality'
    creation_date = 'Mar 29, 2013'
    authors = ['Cornel Nitu']
    description = ('Adding the WebEx planning email functionality')

    def _update(self, portal):
        portal.notify_on_webex_email = ''
        portlets_tool = portal.getPortletsTool()
        menunav_links = portlets_tool['menunav_links']
        menunav_links.manage_add_link_item(id='webex',
        						title='WebEx planning mail',
        						description='',
        						url='/admin_webex_mail_html',
        						relative='1',
        						permission='Naaya - Publish content',
        						order='55')
        self.log.debug('Done')
        return True
