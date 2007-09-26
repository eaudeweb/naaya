for portal in container.get_portals(exclude=False):
  formstool_ob = portal.portal_forms
  if not hasattr(formstool_ob.form_languages_box, 'title'):
    print 'added: %s' % portal.absolute_url(1)
    formstool_ob.manage_addTemplate(id='form_languages_box', title='Box for changing the language when translating content', file='')
    formstool_ob.form_languages_box.pt_edit(text=container.get_fs_data('Products/Naaya/skel/forms/form_languages_box.zpt'), content_type='')

print 'Done.'
return printed
