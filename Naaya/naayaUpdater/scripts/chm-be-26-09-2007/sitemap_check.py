for portal in container.get_portals(exclude=False):
  print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
  print '<br />'
  print hasattr(portal, 'sitemap_xml')
  print '<br />'

print 'Done.'
return printed
