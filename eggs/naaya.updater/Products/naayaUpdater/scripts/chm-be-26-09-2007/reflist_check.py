for portal in container.get_portals(exclude=False):
  portal_portlets = portal.portal_portlets
  print '---'
  for k in portal_portlets.objectValues('Naaya Ref List'):
    print k.id
return printed
