Buildout in a nutshell
----------------------

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

.. _`buildout configuration`: https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk/


Buildout installes Naaya code and configuration in these locations:
  * ``src`` - location of Naaya packages
  * ``products`` - a Products folder, additional products can be placed here
  * ``parts`` - contains Products folders for each of the products defined
    in the ``[zope-instance]`` section of ``naaya.cfg``. This folder is
    volatile, and may be partly or entirely rebuilt when running bin/buildout.
    Do not expect any changes to this folder to be remembered.
  * ``extfile.ini`` - this file is copied in INSTANCE_HOME and configures
    ExtFile to place files in var/files


The various Naaya Buildout files
--------------------------------

At https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk you can
find the main buildout files for Naaya. A few customized toolkits exist for the
EnviroWindows_, DestiNet_ and SEMIDE_ projects, and in their respective folders
there are README files and project-specific `buildout` configuration files.

.. _EnviroWindows: https://svn.eionet.europa.eu/repositories/Naaya/buildout/envirowindows/
.. _DestiNet: https://svn.eionet.europa.eu/repositories/Naaya/buildout/destinet/
.. _SEMIDE: https://svn.eionet.europa.eu/repositories/Naaya/buildout/semide/
