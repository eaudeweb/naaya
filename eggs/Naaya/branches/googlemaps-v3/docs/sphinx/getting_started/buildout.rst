Install Naaya using zc.buildout
===============================

.. note::

    This is the recommended way to install *Naaya*

The ``recommended`` way to install *Naaya*  is to have a custom python
installation for Naaya projects. The reason for this is to provide a clean and
light-weight python that does not overlap with the system python. If you do not
want to compile the python yourself you can use `virtualenv`_


Building python
----------------

.. note::

    You can skip this section if you use `virtualenv`_

.. note::

    The `recommended` python version is *2.4.6*. 
    Naaya has also been tested on Zope 2.12 with python 2.6.6 but is still 
    under testing stage.

Before we download and install python we need to have the following
dependencies first:

* build-essential (Required to compile python)
* zlib1g-dev (Used for zip support)
* libglib2.0-dev (Required by itools)
* libreadline-dev (Optional: useful for debugging purposes)
* libxslt-dev (Required by `lxml`_)

If you have Ubuntu or Debian, you can install the above deps like this::

    apt-get install build-essential zlib1g-dev libglib2.0-dev libreadline-dev libxslt-dev

Now, after the python is downloaded and unarchived::

    ./configure --prefix=/absolute/path/to/python && make && make install


Installing PIL
-------------------

Naaya also requires PIL to be installed. You can install the latest PIL using pip::

    pip install PIL

Or, if you don't have pip, you can manually install PIL::

    wget http://effbot.org/downloads/Imaging-1.1.7.tar.gz
    tar -xzf Imaging-1.1.7.tar.gz
    cd Imaging-1.1.7
    /absolute/path/to/python setup.py install

Installing Naaya
--------------------

To install *Naaya* using :term:`buildout` we will need a buildout skel::

    svn co https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk/

Read the downloaded `README.rst` to learn what each file is used for.

Bootstraping and running :term:`buildout`::

    /path/to/bin/python/ bootstrap.py -c naaya.cfg
    bin/buildout -c naaya.cfg

Top run *Naaya* now simply::

    bin/zope-instance start

    or

    bin/zope-instance fg

More info on buildout
-----------------------

:term:`Buildout` installs Naaya code and configuration in these locations:

  * ``src`` - location of Naaya packages (developement eggs). This location
    needs to be created manually.

  * ``products`` - a Products folder, additional Zope2 products can be placed
    here.  This location needs to be created manually.

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
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _lxml: http://lxml.de/
