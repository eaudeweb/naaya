Install Naaya using zc.buildout
===============================

.. note::

    This is the recommended way to install *Naaya*

:term:`Buildout` installs Naaya code and configuration in these locations:

  * ``src`` - location of Naaya packages. This location needs to be created manually.
  * ``products`` - a Products folder, additional Zope2 products can be placed here
  * ``parts`` - contains Products folders for each of the products defined
    in the ``[zope-instance]`` section of ``naaya.cfg``. This folder is
    volatile, and may be partly or entirely rebuilt when running bin/buildout.
    Do not expect any changes to this folder to be remembered.

Buildout configuration examples
--------------------------------

There is a default `buildout configuration`_ environment which can be used
to setup a clean *Naaya* environment.

Also a few customized toolkits exist for the EnviroWindows_, DestiNet_ and
SEMIDE_ projects, and in their respective folders there are README files and
project-specific `buildout` configuration files.


.. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout
.. _`plone.recipe.bundlecheckout`: http://pypi.python.org/pypi/plone.recipe.bundlecheckout
.. _ConfigParser: http://docs.python.org/library/configparser
.. _`buildout configuration`: https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk/
.. _EnviroWindows: https://svn.eionet.europa.eu/repositories/Naaya/buildout/envirowindows/
.. _DestiNet: https://svn.eionet.europa.eu/repositories/Naaya/buildout/destinet/
.. _SEMIDE: https://svn.eionet.europa.eu/repositories/Naaya/buildout/semide/
