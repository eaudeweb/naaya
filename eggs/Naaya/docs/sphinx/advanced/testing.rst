Testing Naaya
=============

Test runner
---------------

Naaya uses nose_ via `naaya-nose` package to run its tests. ``naaya-nose``` is
a wrapper around nose_ that starts a Zope instance with an clean in-memory
database and then passes the actual running of tests to nose.

Installation
----------------

`naaya-nose` package assumes a `buildout` installation and needs to know the
name of a Zope instance so it can set up ``sys.path`` and load the Zope
configuration file.

#. To add `naaya-nose` to a `buildout` installation, add the following section,
   assuming your Zope part is called ``zope-instance``::

    [naaya-nose]
    recipe = zc.recipe.egg
    eggs = naaya-nose
    arguments = "zope-instance"

#. Also remember to add ``naaya-nose`` to `parts`::

    [buildout]
        parts = 
        ...
        naaya-nose

#. Run :term:`buildout`::

    bin/buildout

You should now have a ``nynose`` script in the ``bin`` folder.

.. note:: 
   `naaya.content.bfile` package is required to run the tests. \
   This package will be part of Naaya core, but until then,\
   you should add it manually to the ``eggs`` list of the Zope instance.

Running tests
-------------
Simply run ``bin/nynose`` with the names of packages to test::

    bin/nynose --with-naaya-portal naaya Products.Naaya Products.NaayaCore Products.NaayaBase

Configuration files
--------------------

It is also recommended to have nose configuration files to reduce the command line arguments. 
For example let's assume we have a config file called `nose.cfg` in your buildout directory containing::

    [nosetests]
    nologcapture = true
    nocapture = true
    with-naaya-portal = true
    with-naaya-selenium = true
    ny-selenium-browsers = *googlechrome
    ....

Which will reduce the command line argument list to::

    bin/nynose -c nose.cfg naaya Products.Naaya Products.NaayaCore Products.NaayaBase

See also
----------

* nose package: nose_
* ``naaya-nose`` package: https://github.com/eaudeweb/naaya-nose/
* ``naaya.selenium`` package: https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/naaya.selenium/

.. _`nose`: http://somethingaboutorange.com/mrl/projects/nose/
