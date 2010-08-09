Testing Naaya
=============

Setting up requirements
-----------------------
Naaya tests are run with the help of the `naaya-nose` package. Its purpose is
to start up a Zope instance with an in-memory database, and then pass control
to `nose` for the actual running of tests. `naaya-nose` assumes a `buildout`
installation and needs to know the name of a Zope instance so it can set up
``sys.path`` and load the Zope configuration file.

To add `naaya-nose` to a `buildout` installation, add the following section,
assuming your Zope part is called ``zope-instance``::

    [naaya-nose]
    recipe = zc.recipe.egg
    eggs = naaya-nose
    arguments = "zope-instance"

Don't forget to add ``naaya-nose`` to the list in `buildout`, `parts` and to
run ``bin/buildout``. You should now have a ``nynose`` script in the ``bin``
folder.

Running tests
-------------
Simpy run ``bin/nynose`` with the names of packages to test::

    bin/nynose naaya Products.Naaya Products.NaayaCore Products.NaayaBase
