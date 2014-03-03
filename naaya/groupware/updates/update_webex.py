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

class UpdateWebExLink(UpdateScript):
    """ """
    title = 'Display the link to WebEx planing for Contributors'
    creation_date = 'Mar 3, 2014'
    authors = ['Valentin Dumitru']
    description = ('Display the link to WebEx planing for Contributor')

    def _update(self, portal):
        portlets_tool = portal.getPortletsTool()
        menunav_links = portlets_tool['menunav_links']
        for link_id, link in menunav_links.get_links_collection().items():
            if link.title == 'WebEx planning mail':
                if link.permission == 'Naaya - Skip approval':
                    self.log.debug('Permission already updated')
                else:
                    item= link.id
                    portal.admin_editlink(id='menunav_links',
                                            item=item,
                                            title='WebEx planning mail',
                                            description='',
                                            url='/admin_webex_mail_html',
                                            relative='1',
                                            permission='Naaya - Skip approval',
                                            order='55')
                break
        else:
            self.log.error('Link with title "WebEx planning mail" not found in '
                            'menunav_links, run UpdateWebEx update first')
        return True


