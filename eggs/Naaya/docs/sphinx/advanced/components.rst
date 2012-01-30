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


.. _bundles:

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


Zope 3 APIs
-----------
Naaya provides the following ZCML directives in the
``http://namespaces.zope.org/naaya`` namespace:

`naaya:call`
    Call a function at Zope startup time. Useful for any kind of
    initialization.

    .. code-block:: xml

        <configure xmlns:naaya="http://namespaces.zope.org/naaya">
            <naaya:call factory="module_name.func_name" />
        </configure>

    .. code-block:: python

        def func_name():
            print "I get called at startup."

`naaya:simpleView`
    Register a function as a Zope 3 View. The function will be called with two
    arguments: `context` and `request`. `permission` is optional, defaults to
    ``zope.Public``.

    .. code-block:: xml

        <configure xmlns:naaya="http://namespaces.zope.org/naaya">
            <naaya:simpleView
                for="Products.Naaya.interfaces.INySite"
                name="hello.html"
                handler="module_name.say_hello"
                permission="zope2.ViewManagementScreens" />
        </configure>

    .. code-block:: python

        def say_hello(context, request):
            return "Hello from <tt>%s</tt>" % '/'.join(context.getPhysicalPath())

    Unlike the Zope 2 publisher, where ``index_html`` is the default page name,
    in Zope 3 the default is ``index.html``. It can be overridden with the
    ``browser:defaultView`` directive:

    .. code-block:: xml

        <configure xmlns:browser="http://namespaces.zope.org/browser">
            <browser:defaultView
                for="Products.Naaya.interfaces.INySite"
                name="hello.html" />
        </configure>

`naaya:rstkMethod`
    Register a method on :term:`RestrictedToolkit`. The method will be
    accessible to any :term:`RestrictedPython` code publicly.

    `name` defaults to the handler's ``__name__`` attribute. `handler` is
    typically a function. If `context` is true, `handler` will be invoked with
    the :class:`~naaya.core.zope2util.RestrictedToolkit` object as first
    argument; defaults to ``no``. `bundle` controls in which :ref:`bundle
    <bundles>` the method will be registered; defaults to ``Naaya``.

    .. code-block:: xml

        <configure xmlns:naaya="http://namespaces.zope.org/naaya">
            <naaya:rstkMethod
                name="complex_action"
                handler="module_name.perform_complex_action"
                context="yes"
                bundle="CHM3" />
        </configure>

    The method can be invoked as follows (`rstk` is acquired from the parent
    :class:`~Products.Naaya.NySite.NySite` object). Note the dictionary-like
    syntax, to emphasize that a component lookup is being performed, instead of
    a simple method access. The method is looked up in the current portal's
    bundle.

    .. code-block:: html

        <tal:block content="python:here.rstk['complex_action']('foo', bar=13)"/>
