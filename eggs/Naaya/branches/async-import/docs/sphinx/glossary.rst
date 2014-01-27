Glossary
========

Some terms used in the documentation are described here.

.. glossary::

    Zope2
        Zope is a Python-based application server for building secure and highly scalable web applications.

    Zope3
        The next version on Zope. However, it is mostly used with Zope2 combined through :term:`Five` or standalone

    Five
        The glue between Zope2 and Zope3 applications

    ZMI
        Zope Management Interface. Specific to Zope2, an interface which allows
        advanced usage of Zope. Things such as adding new instances of products,
        database indexes and connections, template customizations and
        many others.

    Buildout
        The zc.buildout_ package is a tool for deploying complex Python-based
        systems. It was developed to help install Zope and Plone sites, but is being
        used for various repetitive tasks where a predictable result is required.

        In a nutshell, `buildout` reads a configuration file, and invokes various
        `recipes` to perform the actions described in the configuration file. The
        configuration is made up of `parts`, which can be Python packages, Zope
        instances, non-Python applications (an Apache or MySQL instance), startup
        scripts, etc.

        When run for the first time, `buildout` will create the setup "from scratch",
        downloading any required packages. On subsequent runs, it only re-installs parts
        whose configuration has changed [1]_.

        The configuration file is formatted as ``.cfg`` (the format understood by
        ConfigParser_). Each `part` has its own section, describing the `recipe` to be
        used for that part, and a number of recipe-specific configuration options.
        There is also a top-level ``[buildout]`` section used by `buildout` itself.

    ZODB
        A native object database, that stores your objects while allowing you
        to work with any paradigms that can be expressed in Python.
        Thereby your code becomes simpler, more robust and easier to understand.
        Also, there is no gap between the database and your program:
        no glue code to write, no mappings to configure.

        Read the `ZODB book`_ to find out more.

    ZCA
        Zope Component Architecture (ZCA) is a Python framework for supporting
        component based design and programming. It is very well suited to
        developing large Python software systems. The ZCA is not specific to
        the Zope web application server: it can be used for developing any
        Python application. Maybe it should be called as Python Component
        Architecture. Learn more about it at: http://www.muthukadan.net/docs/zca.html

    ZCML
        The Zope Configuration Markup Language (ZCML) is an XML based
        configuration system for registration of components.
        So, instead of using Python API for registration, you can use ZCML.

    CMF
        Content Management Framework

    Role
        User role or user access level. A role is usually used to give specific
        permissions to a group of users. For example `administrators` role
        will have full-control over the site and `normal` role users can just
        add content.

    Content type
        Content types (at least in the context of Naaya) denote types of
        documents or files that can be added in a folder or portal. For example:
        HTML Document, File, Folder, etc.

    WYSIWYG
        What You See Is What You Get.

    Portal
        A portal is synonymous to a site.

    RestrictedPython
        Python code that is executed with reduced privileges. Used in
        Zope2-style page templates and Python code stored in the database.

    RestrictedToolkit
        A singleton object that is available in :term:`RestrictedPython`. See
        the API documentation for :ref:`restricted-toolkit`.

    rstk
        See :term:`RestrictedToolkit`.

    TAL
        Template Attribute Language is an AttributeLanguage used to create 
        dynamic templates. By marking elements of your HTML or XML document 
        with TAL statement attributes, you can replace parts of the document 
        with dynamically computed content.

    ZPT
        Zope Page Template - the default templates in Zope framework


    Site manager
        Another name for a :term:`ZCA` component registry. Site managers hold
        a catalogue of utilities and adapters. See the `ZCA guide`_ for a
        description of its API. The documentation of zope.component_ might
        also be useful.

    Global site manager
        The default :term:`Site manager` of Zope. This is where ZCML
        directives register components. It's not persisted in any ZODB, rather
        it's re-created at every application start-up. The global
        :func:`getUtility`, :func:`getAdapter` etc. functions all use the
        global site manager. To access it explicitly, call
        :func:`zope.component.getGlobalSiteManager`.

    Local site manager
        A :term:`Site manager` that is persisted in ZODB. In Naaya, each
        portal has its own local site manager, that inherits from the
        :term:`Global site manager`. Local site managers are implemented by the
        zope.site_ package.

    Bundle
        A :term:`site manager` that inherits from other bundles, or from the
        :term:`global site manager`.

    Naaya Updates
        There is a product named :doc:`naaya.updater </advanced/updating>`
        that helps you manage update procedures.
        Updates are looked up in all your installed packages. These
        scripts usually apply significant changes and some are required for
        fixing backwards compatibility issues when updating a product.


.. [1] Some recipes, e.g. plone.recipe.bundlecheckout, update their `part`
       on each run of `buildout`.
.. _`ZODB book`: http://readthedocs.org/docs/zodb-documentation/latest/index.html
.. _`ConfigParser`: http://docs.python.org/library/configparser.html
.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout
.. _`ZCA guide`: http://www.muthukadan.net/docs/zca.html
.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.site: http://pypi.python.org/pypi/zope.site
