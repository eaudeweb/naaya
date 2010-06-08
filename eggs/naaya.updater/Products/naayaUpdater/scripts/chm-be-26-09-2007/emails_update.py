for portal in container.get_portals(exclude=False):
  portal_email = portal.portal_email
  portal_email.email_requestrole.manageProperties(title='Request role', body=container.get_fs_data('Products/Naaya/skel/emails/email_requestrole.txt'))

print 'Done.'
return printed
