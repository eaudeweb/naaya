Building the documentation
==========================

Setting up requirements
-----------------------

This documentation is built using `collective.recipe.sphinxbuilder`_ which
is a recipe for `zc.buildout`_ making it easy to build a sphinx documentation.
To build Naaya's documentation, you will need naaya setup in a development
environment. Default naaya buildout checkout provides a `docs.cfg`
which contains a part named `naaya-docs` similar to this one::

    [naaya-docs]
    recipe = collective.recipe.sphinxbuilder
    source = ${buildout:directory}/src/Naaya/docs/sphinx
    build = ${buildout:directory}/var/docs
    extra-paths =
        ${zope-instance:zope2-location}/lib/python
    eggs =
        ${zope-instance:eggs}
        repoze.sphinx.autointerface

Some clarifications:

    * `repoze.sphinx.autointerface` egg is a sphinx extension that
      auto-generates API docs from Zope interfaces
    * `extra-paths` contains the paths that will be loaded into the `sphinx-builder`
      `sys.path` so that it can run docutils against the Naaya source. If these
      paths are not provided, Sphinx will not know where from to import the source.


Check the installation section to see how to install Naaya in a development
environment.

Building the documentation
---------------------------

Simpy run ``bin/naaya-docs``

If you used the above configuration you will find in your buildout directory
under var/docs builder documentation.

.. _collective.recipe.sphinxbuilder: http://pypi.python.org/pypi/collective.recipe.sphinxbuilder/
.. _zc.buildout: http://pypi.python.org/pypi/zc.buildout
