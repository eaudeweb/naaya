Installing Naaya using `zc.buildout`
====================================

.. toctree::
    :hidden:

    buildout_windows

Quick overview of `zc.buildout`
-------------------------------
The `zc.buildout`_ package is a tool for deploying complex Python-based
systems. It was developed to help instal Zope and Plone sites, but is being
used for various repetitive tasks where a predictable result is required.

In a nutshell, `buildout` reads a configuration file, and invokes various
`recipes` to perform the actions described in the configuration file. The
configuration is made up of `parts`, which can be Python packages, Zope
instances, non-Python applications (an Apache or MySQL instance), startup
scripts, etc.

When run for the first time `buildout` will create the setup "from scratch",
downloading any required packages. On subsequent runs it only reinstalls parts
whose configuration has changed [1]_.

The configuration file is formatted as ``.cfg`` (the format understood by
ConfigParser_). Each `part` has its own section, describing the `recipe` to be
used for that part, and a number of recipe-specific configuration options.
There is also a top-level ``[buildout]`` section used by `buildout` itself.

.. [1] Some recipes, e.g. `plone.recipe.bundlecheckout`_, update their `part`
       on each run of `buildout`.
.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout
.. _`plone.recipe.bundlecheckout`: http://pypi.python.org/pypi/plone.recipe.bundlecheckout
.. _ConfigParser: http://docs.python.org/library/configparser


Installing Naaya
----------------
The basic steps for installing Naaya using `buildout` are described in the
`README.txt`_ file. These should work on most Unix-like systems that have
``GLib`` installed. For a detailed guide on the Windows installation process,
see :doc:`buildout_windows`.

.. _`README.txt`: https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk/README.txt
