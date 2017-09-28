"""
Bundles are extra component registries that can be mixed and matched.
Conceptually based on the `z3c.baseregistry` package.
"""
from zope.component import globalregistry, getGlobalSiteManager
from zope.interface import implements
from interfaces import IBundle, ICustomize

class Bundle(globalregistry.BaseGlobalComponents):
    """
    A Naaya bundle of components. Bundle implements the
    `zope.component.interfaces.IComponents` interface, so it handles component
    registration and lookup.
    """
    implements(IBundle)

    def __init__(self, *args, **kwargs):
        super(Bundle, self).__init__(*args, **kwargs)
        self.set_parent(getGlobalSiteManager())

    def __reduce__(self):
        # Global site managers are pickled as global objects
        return get, (self.__name__,)

    def set_parent(self, parent_bundle):
        """
        `parent_bundle` becomes this bundle's new parent. If a component is not
        found in this bundle then it will be searched in the parent.
        """
        self.__bases__ = (parent_bundle,)

    def get_parent(self):
        return self.__bases__[0]


def get(name):
    """
    Get the `name` :class:`Bundle`. If the bundle does not exist, it's created
    and stored in the :term:`global site manager`.
    """
    gsm = getGlobalSiteManager()
    bundle = gsm.queryUtility(IBundle, name=name)
    if bundle is None:
        bundle = Bundle(name)
        gsm.registerUtility(bundle, IBundle, name=name)
    return bundle


def customize_utility(site_manager, util_interface, name):
    """
    Take a named utility, registered in a bundle. Create a copy and store the
    copy in a local site manager.
    """
    orig = site_manager.getUtility(util_interface, name=name)
    customizer = site_manager.getAdapter(orig, ICustomize)
    customizer.customize(site_manager, name)
