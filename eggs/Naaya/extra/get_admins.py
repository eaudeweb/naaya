""" Get all IG Administrators in the EEA """
from naaya.core.zope2util import users_in_role
from Products.Naaya.interfaces import INySite

for ob in app.objectValues():
    if INySite.providedBy(ob):
        admins = users_in_role(ob, 'Administrator')
        for ad in admins:
            if ad.email.endswith('@eea.europa.eu'):
                print "\"%s\", %s, %s" % (ob.title_or_id(), ad.full_name, ad.email)
        group_roles = getattr(ob, '__ny_ldap_group_roles__', None)
        if group_roles:
            for gr, roles in group_roles.items():
                if 'Administrator' in roles:
                    print ("\"%s\", %s, %s@roles.eea.eionet.europa.eu" %
                           (ob.title_or_id(), gr, gr))

