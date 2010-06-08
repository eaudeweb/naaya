for portal in container.get_portals(exclude=False):
    for media_ob in portal.getCatalogedObjects('Naaya Media File'):
        print media_ob.absolute_url()
return printed