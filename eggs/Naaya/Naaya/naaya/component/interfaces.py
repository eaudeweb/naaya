from zope.interface import Interface, Attribute

class IBundle(Interface):
    def set_parent(parent_bundle):
        """ Configure this bundle to inherit from `parent_bundle` """

class ICustomize(Interface):
    def customize(site, name):
        """ Customize the adapted component in `site` with the given name. """

class IDiff(Interface):
    """Diff support"""

    item1 = Attribute("""source of the first item""")
    item2 = Attribute("""source of the second item""")

    html_diff = Attribute("""html diff of two items""")

class IBundleReloader(Interface):
    """ Reloader for a named bundle """
    def reload():
        """ Reload the bundle's components from disk """
