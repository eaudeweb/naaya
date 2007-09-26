for portal in container.get_portals(exclude=False):
  portal_email = portal.portal_email
  print container.show_diffTemplates('Products/Naaya/skel/emails/email_requestrole.txt', portal_email.email_requestrole.absolute_url(1))
return printed
