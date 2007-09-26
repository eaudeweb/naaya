CALENDAR_CSS = """/style_handheld" />
	<link rel="stylesheet" type="text/css" tal:attributes="href string:${site_url}/portal_calendar/calendar_style" />"""
FOOTER_BCH_ORIG = """</div>
</body>
</html>"""
FOOTER_BCH_NEW = """</div>
<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
</script>
<script type="text/javascript">
_uacct = "UA-1814734-1";
urchinTracker();
</script>
</body>
</html>"""
FOOTER_TUNISIE = """Accessibility statement</a>]
[<a tal:attributes="href string:${site_url}/info/chmcoop" accesskey="0" i18n:translate="">CHM cooperation with Belgium</a>]
"""

for portal in container.get_portals():
  portal_layout = portal.portal_layout.chm

  #CSS update
  portal_layout.blue.style.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/blue/style.css'), content_type='')
  portal_layout.blue.style_handheld.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/blue/style_handheld.css'), content_type='')
  portal_layout.brown.style.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/brown/style.css'), content_type='')
  portal_layout.brown.style_handheld.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/brown/style_handheld.css'), content_type='')
  portal_layout.green.style.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/green/style.css'), content_type='')
  portal_layout.green.style_handheld.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/green/style_handheld.css'), content_type='')
  portal_layout.indigo.style.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/indigo/style.css'), content_type='')
  portal_layout.indigo.style_handheld.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/indigo/style_handheld.css'), content_type='')


  #layout JS update
  if portal.absolute_url(1) in  ['zambia/mtenr','formation_chm_madagascar/mauritius','formation_chm_madagascar/madagasca']:
    portal_layout.manage_addTemplate(id='script_dropdownmenus_js', title='Script for dropdown menu', file='')
    portal_layout.manage_addTemplate(id='script_expandableportlets_js', title='Script for expandable portlets', file='')
    portal_layout.script_dropdownmenus_js.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/script_dropdownmenus_js.zpt'), content_type='')
    portal_layout.script_expandableportlets_js.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/script_expandableportlets_js.zpt'), content_type='')
  if portal.id in ['rdcongo2','basissite','comifac','macolloq','formation_chm_madagascar']:
    portal_layout.script_dropdownmenus_js.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/script_dropdownmenus_js.zpt'), content_type='')
  if portal.id in ['benin','rdcongo2','basissite','comifac','macolloq','formation_chm_madagascar','benlcoop']:
    portal_layout.script_expandableportlets_js.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/script_expandableportlets_js.zpt'), content_type='')


  #portlet_center_macro update
  if portal.absolute_url(1) in ['zambia/mtenr','rdcongo2','basissite','comifac','macolloq','formation_chm_madagascar','formation_chm_madagascar/mauritius','formation_chm_madagascar/madagasca']:
    portlet_data = container.get_fs_data('Products/CHM2/skel/layout/chm/portlet_center_macro.zpt')
    portal_layout.portlet_center_macro.pt_edit(text=portlet_data, content_type='text/html')

  #folder_administration_macro update
  portal_layout.manage_addTemplate(id='folder_administration_macro', title='Folder administration macro page', file='')
  portal_layout.folder_administration_macro.pt_edit(text=container.get_fs_data('Products/Naaya/skel/layout/skin/folder_administration_macro.zpt'), content_type='text/html')

  #site_footer update
  footer_data = container.get_fs_data('Products/CHM2/skel/layout/chm/site_footer.zpt')
  if portal.id == 'bch-cbd':
    footer_data = footer_data.replace(FOOTER_BCH_ORIG, FOOTER_BCH_NEW)
    portal_layout.site_footer.pt_edit(text=footer_data, content_type='text/html')
  elif portal.id == 'tunisie':
    footer_data = footer_data.replace('Accessibility statement</a>]', FOOTER_TUNISIE)
    portal_layout.site_footer.pt_edit(text=footer_data, content_type='text/html')
  else:
    portal_layout.site_footer.pt_edit(text=footer_data, content_type='text/html')

  #site_header update
  if not (portal.id in ['niger','civoire','benin','zambia','burundi','maroc']):
    portal_layout.site_header.pt_edit(text=container.get_fs_data('Products/CHM2/skel/layout/chm/site_header.zpt'), content_type='text/html')

  #portals with calendar CSS included in site_header
  if portal.id in ['niger','civoire','benin','zambia','burundi','maroc']:
    header_data = container.get_fs_data('Products/CHM2/skel/layout/chm/site_header.zpt')
    header_data = header_data.replace('/style_handheld" />', CALENDAR_CSS)
    portal_layout.site_header.pt_edit(text=header_data, content_type='text/html')

print 'Done.'
return printed
