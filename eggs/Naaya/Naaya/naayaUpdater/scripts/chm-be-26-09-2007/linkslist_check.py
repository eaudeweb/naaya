linkslist_ids = ['topnav_links','menunav_links','menunav_services','menunav_content','menunav_about','menunav_sitemap']

for portal in container.get_portals(exclude=False):
  portal_portlets = portal.portal_portlets
  print '--- %s ---' % portal.absolute_url(1)
  items = portal_portlets.objectValues('Naaya Links List')
#  print len(items)
  for k in items:
    if k.id == 'menunav_services':
      print 'ura'

return printed
