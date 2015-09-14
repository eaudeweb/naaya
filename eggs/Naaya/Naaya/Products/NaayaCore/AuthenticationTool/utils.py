def _decode(val, encoding_schema='utf-8'):
    if val is None:
        return ''

    if isinstance(val, unicode):
        return val

    return val.decode(encoding_schema)


def schemaHasParam(acl_folder, param):
    for item in acl_folder.getLDAPSchema():
        if item[0] == param:
            return True
    return False


def getUserFullName(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        username = auth_tool.getUserFullName(local_user)
        return _decode(username)

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        if schemaHasParam(acl_folder, 'cn'):
            user = acl_folder.getUserById(uid, None)
            if user is not None:
                return _decode(user.getProperty('cn'), source.default_encoding)


def getUserEmail(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        return auth_tool.getUserEmail(local_user)

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        if schemaHasParam(acl_folder, 'mail'):
            user = acl_folder.getUserById(uid, None)
            if user is not None:
                return _decode(user.getProperty('mail'),
                               source.default_encoding)


def getUserOrganization(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        return ''

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        if schemaHasParam(acl_folder, 'o'):
            user = acl_folder.getUserById(uid, None)
            if user is not None:
                return _decode(user.getProperty('o'), source.default_encoding)


def getUserPhoneNumber(site, uid):
    auth_tool = site.getAuthenticationTool()
    local_user = auth_tool.getUser(uid)
    if local_user is not None:
        return ''

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        if schemaHasParam(acl_folder, 'telephoneNumber'):
            user = acl_folder.getUserById(uid, None)
            if user is not None:
                return _decode(user.getProperty('telephoneNumber'),
                               source.default_encoding)


def findUsers(site, search_param, search_term):
    def userMatched(uid, cn):
        if not search_term:
            return False
        if search_param == 'uid':
            return search_term in uid
        elif search_param == 'cn':
            return search_term.encode('utf-8') in cn.encode('utf-8')
        else:
            return False

    auth_tool = site.getAuthenticationTool()
    ret = []

    for user in auth_tool.getUsers():
        uid = auth_tool.getUserAccount(user)
        cn = auth_tool.getUserFullName(user)
        mail = getUserEmail(site, uid)
        info = 'Local user'

        if userMatched(uid, cn):
            ret.append({
                'uid': uid,
                'cn': cn,
                'mail': mail,
                'organization': '',
                'info': info})

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        if schemaHasParam(acl_folder, search_param):
            users = acl_folder.findUser(
                search_param=search_param,
                search_term=search_term.encode('utf-8'))
            for user in users:
                uid = user.get('uid', '')
                cn = _decode(user.get('cn', ''), source.default_encoding)
                mail = user.get('mail', '')
                organization = _decode(user.get('o', ''),
                                       source.default_encoding)
                info = user.get('dn', '')
                ret.append({
                    'uid': uid,
                    'cn': cn,
                    'mail': mail,
                    'organization': organization,
                    'info': info
                })

    return ret


def listUsersInGroup(site, search_role):
    auth_tool = site.getAuthenticationTool()
    ret = []

    for source in auth_tool.getSources():
        acl_folder = source.getUserFolder()
        users = source.getUsersByRole(acl_folder, [(search_role, None)])
        for user in users:
            ret.append({
                'uid': user.user_id,
                'cn': _decode(user.full_name, source.default_encoding),
                'organization': _decode(user.organisation,
                                        source.default_encoding),
                'info': user.dn,
                'mail': user.email,
            })

    return ret
