# Example code:

# Import a standard function, and get the HTML request and response objects.
request = container.REQUEST
RESPONSE =  request.RESPONSE

#for portal in container.get_portals(exclude=False):
#    portal_syndication = portal.portal_syndication
#    try:
#        url =  portal_syndication.upcomingevents_rdf.absolute_url(1)
#    except AttributeError:
#        url = None
#    if url is not None:
#        #print portal_syndication.absolute_url()
#        print container.show_diffTemplates('Products/Naaya/skel/syndication/upcomingevents_rdf.py', url)
#    else:
#        print 'err: %s' % portal_syndication.absolute_url()
#    print '<br />'
#return printed


#for portal in container.get_portals(exclude=False):
#    portal_portlets = portal.portal_portlets
#    try:
#        url =  portal_portlets.portlet_upcomingevents_rdf.absolute_url(1)
#    except AttributeError:
#        url = None
#    if url is not None:
#        print portal_portlets.absolute_url()
#        print container.show_diffTemplates('Products/Naaya/skel/syndication/upcomingevents_rdf.zpt', url)
#    else:
#        print 'err: %s' % portal_portlets.absolute_url()
#    print '<br />'
#return printed


#exclude_list = ['latestrelevantuploads_rdf', 'meetingsevents_rdf', 'whatsnew_rdf', 'latestnews_rdf', 'lateststories_rdf', 'latestuploads_rdf', 'upcomingevents_rdf']
#for portal in container.get_portals(exclude=False):
#    portal_syndication = portal.portal_syndication
#    for script in portal_syndication.objectValues('Naaya Script Channel'):
#        if script.id not in exclude_list:
#            print 'err: %s' % script.absolute_url()
#    print '\n'
#return printed

exclude_list = ['portlet_latestrelevantuploads_rdf', 'portlet_meetingsevents_rdf', 'portlet_whatsnew_rdf', 'portlet_latestnews_rdf', 'portlet_lateststories_rdf', 'portlet_latestuploads_rdf', 'portlet_upcomingevents_rdf']
for portal in container.get_portals(exclude=False):
    portal_portlets = portal.portal_portlets
    for script in portal_portlets.objectValues('Naaya Portlet'):
        if script.id not in exclude_list or not script.id.endswith('_rdf'):
            print 'err: %s' % script.absolute_url()
    print '\n'
return printed
