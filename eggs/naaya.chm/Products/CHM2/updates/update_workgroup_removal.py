from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateWorkgroupRemoval(UpdateScript):
    """ """
    title = 'Cleanup workgroup attributes and portlet administration'
    creation_date = 'Oct 28, 2011'
    authors = ['Andrei Laza']
    priority = PRIORITY['LOW']

    def _update(self, portal):
        if hasattr(portal.aq_base, 'workgroups'):
            self.log.debug('removing "workgroups" attribute')
            del portal.workgroups
        else:
            self.log.debug('no need to remove "workgroups" attribute')

        portlets = portal.portal_portlets
        if portlets.hasObject('portlet_administration'):
            self.log.debug('portlet_administration is customized on this portal')
            workgroups_link = '<a tal:attributes="href string:${site_url}/admin_workgroups_html" title="Workgroups" i18n:attributes="title" i18n:translate="">Workgroups</a>'
            portlet_source = portlets.portlet_administration.read()
            if portlet_source.find(workgroups_link) != -1:
                local_roles_link = '<a tal:attributes="href string:${site_url}/admin_folders_with_local_roles" title="Folders with local roles" i18n:attributes="title" i18n:translate="">Local roles</a>'
                portlet_source = portlet_source.replace(workgroups_link, local_roles_link)
                portlets.portlet_administration.write(portlet_source)
                self.log.debug('replaced workgroups link with local roles link in portlet source')
            else:
                self.log.warning('could not find workgroups link in portlet source; check manually %s/pt_editForm', portlets.portlet_administration.absolute_url())
        else:
            self.log.debug('portlet_administration not customized, no need to change it')
        return True
