Installing Envirowindows
========================

To install CHM Biodiv please refer to `Installing Naaya
<http://naaya.eaudeweb.ro/docs/installation.html>`_, while using the
provided configuration file ``chm.cfg``::

    #Create a symlink so you know which buildout was used for future updates
    ln -s chm.cfg buildout.cfg
    python bootstrap.py
    bin/buildout
    bin/zope-instance start #To start the Zope Server

For production enviroments it is recomended to use ZEO configuration file 
``chm-zeo.cfg``::

    ln -s chm-zeo.cfg buildout.cfg
    python bootstrap.py
    bin/buildout
    bin/zeo-server start #First ZEO server must be started
    bin/zope-instance1 start
    bin/zope-instance2 start
