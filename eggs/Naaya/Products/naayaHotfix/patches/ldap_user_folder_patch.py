from zLOG import LOG, INFO, DEBUG


def patch_ldap_user_folder():
    try:
        from Products.LDAPUserFolder import utils
        ldap_user_folder_installed = True
    except ImportError:
        ldap_user_folder_installed = False

    if ldap_user_folder_installed:
        utils.encoding = 'utf-8'

    LOG('naayaHotfix', DEBUG,
        'Patched Products.LDAPUserFolder encoding to utf-8')
    LOG('naayaHotfix', INFO,
        'Patched Products.LDAPUserFolder encoding to utf-8')
