Glossary
========

Some terms used in the documentation are described here.

.. glossary::

    Zope2
        Zope is a Python-based application server for building secure and highly scalable web applications.

    zope3
        The next version on Zope. However it is mostly used with Zope2 combined through :term:`Five` or standalone

    Five
        The glue between Zope2 and zope3 applications

    ZMI
        Zope Management Interface. Specific to Zope2, an interface which allows
        advanced usage of Zope. Things such as adding new instantaces of products.
        database indexes and connections, template customizations and
        many others.

    Buildout
        The `zc.buildout`_ package is a tool for deploying complex Python-based
        systems. It was developed to help install Zope and Plone sites, but is being
        used for various repetitive tasks where a predictable result is required.

        In a nutshell, `buildout` reads a configuration file, and invokes various
        `recipes` to perform the actions described in the configuration file. The
        configuration is made up of `parts`, which can be Python packages, Zope
        instances, non-Python applications (an Apache or MySQL instance), startup
        scripts, etc.

        When run for the first time `buildout` will create the setup "from scratch",
        downloading any required packages. On subsequent runs it only re-installs parts
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

.. [1] Some recipes, e.g. `plone.recipe.bundlecheckout`_, update their `part`
       on each run of `buildout`.
.. `ZODB book` http://readthedocs.org/docs/zodb-documentation/latest/index.html
