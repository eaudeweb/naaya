# !!!! These should be moved to auth_tool

def _encode(val):
    if isinstance(val, unicode):
        return val.encode('utf-8')
    return unicode(val, 'iso-8859-1').encode('utf-8')

def getUserFullName(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        username = auth_tool.getUserFullName(local_user)
        return _encode(username)

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        user = acl_folder.getUserById(uid, None)
        if user is not None:
            return _encode(user.getProperty('cn'))

def getUserEmail(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        return auth_tool.getUserEmail(local_user)

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        user = acl_folder.getUserById(uid, None)
        if user is not None:
            return _encode(user.getProperty('mail'))

def getUserOrganisation(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        return ''

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        user = acl_folder.getUserById(uid, None)
        if user is not None:
            return _encode(user.getProperty('o'))

def getUserPhoneNumber(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        return ''

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        user = acl_folder.getUserById(uid, None)
        if user is not None:
            return _encode(user.getProperty('telephoneNumber'))


