for portal in container.get_portals(exclude=False):
  portal.manage_addProduct['PythonScripts'].manage_addPythonScript(id='sitemap_xml')
  portal.sitemap_xml.ZPythonScript_edit(params='', body=container.get_fs_data('Products/Naaya/skel/others/sitemap_xml'))

print 'Done.'
return printed
