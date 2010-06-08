# Example code:

request = container.REQUEST
RESPONSE =  request.RESPONSE

#latestnews_rdf
#--------------------------------------------------------------
exclude_portal_ids = ['madagascar', 'info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_syndication.latestnews_rdf.write(container.get_fs_data('Products/Naaya/skel/syndication/latestnews_rdf.py'))
print 'Done latestnews_rdf'


#lateststories_rdf
#--------------------------------------------------------------
exclude_portal_ids = ['madagascar', 'info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_syndication.lateststories_rdf.write(container.get_fs_data('Products/Naaya/skel/syndication/lateststories_rdf.py'))
print 'Done lateststories_rdf'


#latestuploads_rdf
#--------------------------------------------------------------
exclude_portal_ids = ['info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_syndication.latestuploads_rdf.write(container.get_fs_data('Products/Naaya/skel/syndication/latestuploads_rdf.py'))
print 'Done latestuploads_rdf'


#upcomingevents_rdf
#--------------------------------------------------------------
exclude_portal_ids = ['madagascar', 'info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_syndication.upcomingevents_rdf.write(container.get_fs_data('Products/Naaya/skel/syndication/upcomingevents_rdf.py'))
print 'Done upcomingevents_rdf'

#++++++++++++++++UPDATE PORTLETS ++++++++++++++++++++++++++++++++++


#portlet_latestrelevantuploads_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_latestrelevantuploads_rdf.pt_edit(text=container.get_fs_data('Products/CHM2/skel/syndication/latestrelevantuploads_rdf.zpt'), content_type='text/html')
print 'Done portlet_latestrelevantuploads_rdf'


#portlet_meetingsevents_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_meetingsevents_rdf.pt_edit(text=container.get_fs_data('Products/CHM2/skel/syndication/meetingsevents_rdf.zpt'), content_type='text/html')
print 'Done portlet_meetingsevents_rdf'

#portlet_whatsnew_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_whatsnew_rdf.pt_edit(text=container.get_fs_data('Products/CHM2/skel/syndication/whatsnew_rdf.zpt'), content_type='text/html')
print 'Done portlet_whatsnew_rdf'

#portlet_whatsnew_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405', 'madagascar']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_latestnews_rdf.pt_edit(text=container.get_fs_data('Products/Naaya/skel/syndication/latestnews_rdf.zpt'), content_type='text/html')
print 'Done portlet_latestnews_rdf'

#portlet_lateststories_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405', 'madagascar']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_lateststories_rdf.pt_edit(text=container.get_fs_data('Products/Naaya/skel/syndication/lateststories_rdf.zpt'), content_type='text/html')
print 'Done portlet_lateststories_rdf'


#portlet_latestuploads_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_latestuploads_rdf.pt_edit(text=container.get_fs_data('Products/Naaya/skel/syndication/latestuploads_rdf.zpt'), content_type='text/html')
print 'Done portlet_latestuploads_rdf'

#portlet_upcomingevents_rdf
#----------------------------------------------------------------
exclude_portal_ids = ['info0405', 'madagascar']
for portal in container.get_portals(exclude=False):
    if portal.id not in exclude_portal_ids:
        portal.portal_portlets.portlet_upcomingevents_rdf.pt_edit(text=container.get_fs_data('Products/Naaya/skel/syndication/upcomingevents_rdf.zpt'), content_type='text/html')
print 'Done portlet_upcomingevents_rdf'

return printed


#++++++++++++++++OTHER PORTLETS ++++++++++++++++++++++++++++++++++
#----------------------------------------------------------------
for portal in container.get_portals(exclude=False):
    for portlet in portal.portal_portlets.objectValues('Naaya Portlet'):
        print portlet.absolute_url()
        content = portlet.document_src()
        content = content.replace('<a tal:attributes="href channel/absolute_url"><img src="misc_/NaayaCore/xml.png" width="36" height="14" border="0" alt="Syndication (XML)" i18n:attributes="alt" /></a>', \
                                  '<a tal:attributes="href channel/absolute_url"><img src="misc_/NaayaCore/xml.png" alt="Syndication (XML)" i18n:attributes="alt" /></a>')
        portlet.pt_edit(text=content, content_type='text/html')
print 'Done other portlets'

return printed
