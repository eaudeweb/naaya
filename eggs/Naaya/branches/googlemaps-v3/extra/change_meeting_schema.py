from Products.Naaya.interfaces import INySite

for site in app.objectValues():
    if INySite.providedBy(site):
        try:
            site.portal_schemas['NyMeeting']['allow_register-property'].sortorder = 147
            site.portal_schemas['NyMeeting']['auto_register-property'].sortorder = 148
        except KeyError:
            print "error in %s" % site
        else:
            'Successful update in %s.' % site

