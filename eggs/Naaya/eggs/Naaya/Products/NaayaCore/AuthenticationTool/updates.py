from Products.naayaUpdater.updates import UpdateScript

permission_map = {
    'Publish content': 'Naaya - Publish content',
}

class RemovePermissionGroups(UpdateScript):
    title = 'Remove permission groups'
    authors = ['Alex Morega']
    creation_date = 'Aug 02, 2010'

    def _update(self, portal):
        portlets_tool = portal.getPortletsTool()

        for links_list in portlets_tool.objectValues(['Naaya Links List']):
            for id, item in links_list.get_links_collection().items():
                old_perm = item.permission
                if (not old_perm) or (old_perm in permission_map.values()):
                    # looks like it has already been updated
                    continue

                new_perm = permission_map[old_perm]
                pth = '/'.join(links_list.getPhysicalPath()) + ':' + id
                self.log.info('%r: %r -> %r', pth, old_perm, new_perm)
                item.permission = new_perm

            links_list._p_changed = True

        return True
