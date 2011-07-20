from zope.interface import Interface


class IBundle(Interface):
    def set_parent(parent_bundle):
        """ Configure this bundle to inherit from `parent_bundle` """

class ICustomize(Interface):
    def customize(site, name):
        """ Customize the adapted component in `site` with the given name. """
