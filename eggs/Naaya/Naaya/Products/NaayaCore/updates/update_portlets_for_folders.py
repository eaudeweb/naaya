from Products.naayaUpdater.updates import UpdateScript

class UpdatePortletsForFolders(UpdateScript):
    title = ('Update portlets created for folders to display content as links')
    description = ('Update portlets created for folders to display content as '
            'links (currently no subobjects are displayed)')
    authors = ['Valentin Dumitru']
    creation_date = 'Jan 29, 2014'

    def _update(self, portal):
        old_tal = ' tal:content="structure folder/description">'
        new_tal = ('>\n      <ul>\n'
                   '        <li tal:repeat="subfolder folder/getPublishedFolders">\n'
                   '          <a tal:attributes="href subfolder/absolute_url;\n'
                   '                             title subfolder/title_or_id"\n'
                   '             tal:content="subfolder/title_or_id" '
                   'i18n:attributes="title"\n'
                   '             i18n:translate="" /></li>\n'
                   '      </ul>\n    ')

        for folder_portlet in portal.getPortletsTool().get_folders_portlets():
            tal = folder_portlet.read()
            if new_tal in tal:
                self.log.debug('Portlet %s already updated' %
                                folder_portlet.getId())
            elif old_tal in tal:
                tal = tal.replace(old_tal, new_tal)
                folder_portlet.write(tal)
                self.log.debug('Portlet %s successfully updated' %
                                folder_portlet.getId())
            else:
                self.log.error('Old and new code not in portlet %s' %
                               folder_portlet.absolute_url())
                return False

        return True
