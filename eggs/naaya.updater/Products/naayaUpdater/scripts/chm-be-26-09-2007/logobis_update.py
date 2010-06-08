for portal in container.get_portals():
  portal_layout = portal.portal_layout
  if hasattr(portal_layout, 'logobis'):
    portal_layout.manage_renameObjects(['logobis'], ['logobis.gif'])

print 'Done.'
return printed

#RUN   #site_header update
#RUN   #portals with calendar CSS included in site_header