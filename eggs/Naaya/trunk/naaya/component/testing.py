from zope import interface
from zope.component import getGlobalSiteManager
from interfaces import IBundle
import bundles



class ITestUtil(interface.Interface):
    """ Blank interface, so we have something to register. """


class MyClass(object):
    """ Simple class that implements `ITestUtil`. """
    interface.implements(ITestUtil)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def clean_up_bundle(name):
    """ Unregister the `name` bundle. """
    gsm = getGlobalSiteManager()
    gsm.unregisterUtility(bundles.get(name), IBundle, name=name)
