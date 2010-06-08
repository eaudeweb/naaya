#55 portals
i = 0
for portal in container.get_portals(exclude=False):
  portal_layout = portal.portal_layout.chm

#  for k in portal.portal_layout.objectValues('Naaya Skin'):
#    if k.id == 'chm':
#      for m in k.objectValues('Naaya Scheme'):
#        if not (m.id in ['blue','brown','green','indigo']):
#          print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
#          print '<br />'
#          print m.id
#          print '<br />'


#  #check scheme
#  print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
#  print '<br />'
#  print len(portal_layout.green.style.document_src())
#  print '<br />'
#  print container.show_diffTemplates('Products/CHM2/skel/layout/chm/green/style_print.css', portal_layout.green.style_print.absolute_url(1))


#  #check layout JS
#  print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
#  print '<br />'
#  print 'script_dropdownmenus_js: %s' % hasattr(portal_layout, 'script_dropdownmenus_js')
#  print '<br />'
#  print 'script_expandableportlets_js: %s' % hasattr(portal_layout, 'script_expandableportlets_js')
#  print '<br />'
#  if portal.id in ['rdcongo2','basissite','comifac','macolloq','formation_chm_madagascar']:
#    print container.show_diffTemplates('Products/CHM2/skel/layout/chm/script_dropdownmenus_js.zpt', portal_layout.script_dropdownmenus_js.absolute_url(1))
#  if portal.absolute_url(1) in ['benin','rdcongo2','basissite','comifac','macolloq','formation_chm_madagascar','benlcoop']:
#    print container.show_diffTemplates('Products/CHM2/skel/layout/chm/script_expandableportlets_js.zpt', portal_layout.script_expandableportlets_js.absolute_url(1))

#  #check site_footer
#  print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
#  print container.show_diffTemplates('Products/CHM2/skel/layout/chm/portlet_right_macro.zpt', portal_layout.portlet_right_macro.absolute_url(1))
#  print container.show_diffTemplates('Products/CHM2/skel/layout/chm/portlet_left_macro.zpt', portal_layout.portlet_left_macro.absolute_url(1))
#  if portal.absolute_url(1) in ['zambia/mtenr','rdcongo2','basissite','comifac','macolloq','formation_chm_madagascar','formation_chm_madagascar/mauritius','formation_chm_madagascar/madagasca']:
#    print container.show_diffTemplates('Products/CHM2/skel/layout/chm/portlet_center_macro.zpt', portal_layout.portlet_center_macro.absolute_url(1))

#  #check folder_administration_macro
#  print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
#  print '<br />'
#  print hasattr(portal_layout, 'folder_administration_macro')
#  print '<br />'

#  #check site_footer
#  print '<span style="color:red">####</span> <b style="color:blue">%s</b>' %portal.absolute_url(1)
#  print container.show_diffTemplates('Products/CHM2/skel/layout/chm/site_footer.zpt', portal_layout.site_footer.absolute_url(1))

  #check site_header
#  if portal.absolute_url(1) in ['niger','civoire','benin','zambia','burundi','maroc']:
  if portal.absolute_url(1) in ['bch-cbd','maroc2','comifac_dev','test_layout_arnaud']:
    print '#### %s' %portal.absolute_url(1)
    print container.show_diffTemplates('Products/CHM2/skel/layout/chm/portlet_center_macro.zpt', portal_layout.portlet_center_macro.absolute_url(1))

return printed
