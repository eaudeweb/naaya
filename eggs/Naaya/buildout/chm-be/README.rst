Installing Belgian CHM
======================

To install Belgian CHM please refer to `Installing Naaya
<http://naaya.eaudeweb.ro/docs/installation.html>`_, while using the
provided configuration file ``chm.cfg``::

    #Create a symlink so you know which buildout was used for future updates
    ln -s chm.cfg buildout.cfg
    python bootstrap.py
    bin/buildout
    bin/zope-instance start #To start the Zope Server
