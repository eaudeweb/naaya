from Products.naayaUpdater.updates import UpdateScript


class UpdateLinksList(UpdateScript):
    """ """
    title = 'Update places and menunav_links'
    creation_date = 'Oct 09, 2019'
    authors = ['Valentin Dumitru']
    description = ('Update places and menunav_links according to requirements')

    def _update(self, portal):
        to_delete = {
            'menunav_links': [('about', 'About'),
                              ('library', 'Library'),
                              ('member_search', 'Member search'),
                              ('events', 'Events'),
                              ('email', 'Email'),
                              ('search', 'IG Search'),
                              ('help', 'Help')],
            'places': [('', 'EWindows'),
                       ('', 'EEA home'),
                       ('', 'Europa'),
                       ('', 'Eionet')
                       ],
        }
        to_update = {
            'places': [
                ['help', 'Eionet Forum - Introduction and help',
                 'Eionet Forum - Introduction and help', '/help', True, '',
                 1],
                ['eionet', 'Eionet Portal', 'Eionet Portal',
                 'https://www.eionet.europa.eu/', False, '', 2],
                ['planner', 'Eionet Planner', 'Eionet Planner',
                 'https://eionetplanner.eionet.europa.eu/', False, '', 3],
                ['helpdesk', 'Eionet Helpdesk', 'Eionet Helpdesk',
                 'https://www.eionet.europa.eu/about/helpdesk', False, '', 4],
            ],
            'menunav_links': [
                ['library', 'Library', 'Library', '/library', True, '', 1],
                ['member_search', 'Member search', 'Member search',
                 '/member_search', True, '', 2],
                ['search', 'Free text search', 'Free text search',
                 '/search_html', True, '', 3],
                ['contact', 'Contact us', 'Contact us', '/about/contact', True,
                 '', 4]
            ]
        }
        p_tool = portal.getPortletsTool()
        for link, new_links in to_update.items():
            links_list = p_tool.getLinksListById(link)
            links_list_items = {lk.title: lk.id for lk in
                                links_list.get_links_list()}
            links_to_delete = to_delete[link]
            for d_link in links_to_delete:
                if d_link[0]:
                    links_list.manage_delete_links(d_link[0])
                    self.log.debug('Deleted link with ID %s' % d_link[0])
                else:
                    d_link_id = links_list_items.get(d_link[1])
                    if d_link_id:
                        links_list.manage_delete_links(d_link_id)
                        self.log.debug(
                            'Deleted link with Title %s' % d_link[1])
                    else:
                        self.log.debug(
                            'No link with Title %s' % d_link[1])
            for new_link in new_links:
                links_list.add_link_item(*new_link)
            self.log.debug('Added %s links in %s' % (len(new_links), link))
        return True
