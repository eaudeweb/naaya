from zope import interface

class INyCatalogAware(interface.Interface):
    """ Object can be indexed in the Naaya catalog """

class INyCatalogIndexing(interface.Interface):
    """ Adapts objects that are about to be indexed (getattr, mainly) """
