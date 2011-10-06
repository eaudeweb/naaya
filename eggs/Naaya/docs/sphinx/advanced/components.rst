.. py:currentmodule:: naaya.component.bundles

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


Component bundles
-----------------
Bundles provide a way to define components and have them apply only to
specific sites. Strictly speaking, a :term:`bundle` is a :term:`site manager`,
with a bit of helper logic to make life easier.


Creating a bundle and registering components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bundles are created by calling :func:`get`. Subsequent requests with the same
name will return the same bundle instance::

    >>> from naaya.component import bundles
    >>> naaya_bundle = bundles.get("Naaya")

To register components in the bundle, use the api of Zope Components::

    >>> # note: the naaya.core.template package is fictional
    >>> from naaya.core.templates import load_template, INyTemplate
    >>> template = load_template('zpt/some_template', __file__, 'some_template')
    >>> naaya_bundle.registerUtility(template, name=template.__name__)
    >>> naaya_bundle.getUtility(INyTemplate, 'some_template') is template
    True

..
..  For registering templates we can also use the `register_template` shortcut::
..
..
..      >>> from naaya.core.templates import register_template
..      >>> register_template(naaya_bundle, 'some_template', 'zpt/some_template', __file__)


Bundle inheritance
~~~~~~~~~~~~~~~~~~
Each bundle has a parent bundle, which is by default the :term:`global site
manager`. Inheritance is configured using :meth:`Bundle.set_parent` and it's
based on Zope Component's `__bases__` mechanism::

    >>> chm_bundle = bundles.get("CHM")
    >>> chm_bundle.set_parent(naaya_bundle)
    >>> chm_bundle.getUtility(INyTemplate, 'some_template') is template
    True


Portal bundle
~~~~~~~~~~~~~
A Naaya :term:`portal` has a :term:`local site manager` which inherits from a
bundle. This bundle is set using :meth:`~Products.Naaya.NySite.set_bundle`::

    >>> # note: in reality, CHM portals are instances of the CHMSite class
    >>> from Products.Naaya.NySite import NySite
    >>> portal = NySite('my-chm-portal')
    >>> portal.set_bundle(chm_bundle)

.. TODO setting a bundle on the portal


Filesystem bundles
~~~~~~~~~~~~~~~~~~
Some installations of Naaya have extensive customizations for templates
and styling. These are stored as separate Python packages in version
control and each contains a number of bundles. Because they do little
more than templates in a bundle, there is common code in Naaya for
loading them (see :func:`~naaya.core.fsbundles.load_filesystem_bundle`)::

    >>> from naaya.component import bundles
    >>> from naaya.core.fsbundles import load_filesystem_bundle
    >>> load_filesystem_bundle('path/to/bespoke.bundle', 'Bespoke')
    >>> bespoke = bundles.get('Bespoke')

Now, if we look in `bespoke`, we find templates registered from
`path/to/bespoke.bundle/templates`. To make use of the templates we need
to configure a Naaya portal to use `Bespoke` as its parent bundle.
