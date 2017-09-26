from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

_admin_assign_role = NaayaPageTemplateFile('zpt/site_admin_editor_role',
                                           globals(), 'site_admin_editor_role')


def admin_assign_role(context, REQUEST):
    """ the method has two ways of working:
        1. it renders a page that allows the administrator to select a
           a contributor and then assign local editor role on the contributed
           objects to another user
        2. if the method's parent is a contact, then use this as the only
           object to be modified"""
    if context.meta_type == 'Naaya Contact':
        contact = context
    else:
        contact = None
    orig_id = REQUEST.get('orig_id')
    object_paths = REQUEST.get('object_paths', [])
    new_users = REQUEST.get('new_users', [])
    messages = []
    options = {}
    user_list = context.getAuthenticationTool().getUsers()
    users = {}
    for user in user_list:
        users[user.name] = {'name': user.firstname + ' ' + user.lastname,
                            'email': user.email}
    user_ids = sorted(users.keys(), key=lambda x: x.lower())
    if orig_id == '':
        if not contact:
            messages.append('Please select a user to search for content.')
        orig_id = None
    options['users'] = users
    options['user_ids'] = user_ids
    options['contact'] = contact
    if not (orig_id or contact):
        options['messages'] = messages
        return _admin_assign_role.__of__(context)(REQUEST, **options)

    if 'assign_role' in REQUEST:
        if isinstance(object_paths, basestring):
            object_paths = [object_paths]
        if isinstance(new_users, basestring):
            new_users = [new_users]
        if not object_paths:
            messages.append(
                'Please select at least one object to assign role to.')
        else:
            options['object_paths'] = object_paths
        if not new_users:
            messages.append(
                'Please select at least one user to assign role to.')
        else:
            options['new_users'] = new_users
        if object_paths and new_users:
            for path in object_paths:
                ob = context.getSite().restrictedTraverse(path)
                for user_id in new_users:
                    ob.manage_setLocalRoles(user_id, ['Editor'])
        if contact and not messages:
            context.setSessionInfoTrans('Editor role assigned successfully')
            return REQUEST.RESPONSE.redirect(context.absolute_url())

    obj_list = context.getCatalogedObjects(contributor=orig_id)
    if not obj_list and not contact:
        messages.append(
            "User %s doesn't have contributions on this site yet." % orig_id)
    objects = []
    for ob in obj_list:
        local_roles = ob.__ac_local_roles__ or {}
        objects.append(['/'.join(ob.getPhysicalPath()), ob.title_or_id(),
                        local_roles])
    if contact:
        objects.append(['/'.join(contact.getPhysicalPath()),
                        contact.title_or_id(),
                        contact.__ac_local_roles__ or {}])
    options['messages'] = messages
    options['objects'] = sorted(objects, key=lambda x: x[1].strip().lower())
    return _admin_assign_role.__of__(context)(REQUEST, **options)
