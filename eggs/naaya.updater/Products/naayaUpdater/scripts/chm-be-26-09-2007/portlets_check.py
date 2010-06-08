for portal in container.get_portals(exclude=False):
  portal_portlets = portal.portal_portlets
#  print '--- %s ---' % portal.id
  items = portal_portlets.objectValues('Naaya Portlet')

#  for k in items:
#    if not (k.id in ['portlet_administration', 'portlet_maincategories', 'portlet_latestphotos', 'portlet_localchannels', 'portlet_folder_administration']):
#      if not k.id.endswith('_rdf'):
#        k_ob = getattr(portal_portlets, k.id)
#        print k.id
#        if k_ob.document_src().find('getSyndicationTool') == -1:
#          print 'nu e rdf'

  for k in items:
    if k.id == 'portlet_localchannels':
      if portal.absolute_url(1) in ['bch-cbd','test_layout_arnaud','comifac_dev','maroc2']:
        print '--- %s ---' % portal.id
        print container.show_diffTemplates('Products/Naaya/skel/portlets/portlet_localchannels.zpt', portal_portlets.portlet_localchannels.absolute_url(1))
return printed
