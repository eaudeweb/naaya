Zope Components in Naaya
========================

Some things in Naaya are discovered using component lookup. Each Naaya site
has a :term:`local site manager` which can override components in the global
site manager. To ensure all components are found, when performing adaptations
and utility lookups, use :func:`~naaya.core.zope2util.get_site_manager`
(`context` is the object being published)::

    from naaya.core.zope2util import get_site_manager
    sm = get_site_manager(context) # get the local site manager
    sm.getUtility(IUsefulStuff) # get a utility
    sm.getAdapter(ob, ISomethingElse) # adapt an object to an interface
