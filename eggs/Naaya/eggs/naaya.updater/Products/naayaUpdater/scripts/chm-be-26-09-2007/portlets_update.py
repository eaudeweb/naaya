for portal in container.get_portals(exclude=False):
  portal_portlets = portal.portal_portlets

  if not (portal.id in ['bch-cbd','test_layout_arnaud','comifac_dev','maroc2']):
    portal_portlets.portlet_administration.pt_edit(text=container.get_fs_data('Products/CHM2/skel/portlets/portlet_administration.zpt'), content_type='text/html')
  if not (portal.id in ['bch-cbd','test_layout_arnaud','comifac_dev','maroc2','test_maroc']):
    portal_portlets.portlet_maincategories.pt_edit(text=container.get_fs_data('Products/CHM2/skel/portlets/portlet_maincategories.zpt'), content_type='text/html')
  if not (portal.id in ['maroc2','comifac_dev']):
    portal_portlets.portlet_latestphotos.pt_edit(text=container.get_fs_data('Products/CHM2/skel/portlets/portlet_latestphotos.zpt'), content_type='text/html')
  portal_portlets.portlet_localchannels.pt_edit(text=container.get_fs_data('Products/Naaya/skel/portlets/portlet_localchannels.zpt'), content_type='text/html')
  portal_portlets.create_portlet_special('portlet_folder_administration', 'Folder Administration', container.get_fs_data('Products/Naaya/skel/portlets/portlet_folder_administration.zpt'))

print 'Done.'
return printed
