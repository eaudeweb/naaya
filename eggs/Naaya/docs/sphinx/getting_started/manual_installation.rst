Manual installation
====================

.. deprecated:: 2.11.03
    This document is outdated and will most likely not work.

So you don't like `buildout` and want to install Naaya manually. Here's a
step-by-step guide, using `virtualenv`_. It assumes you already have a
working python (=>2.4 or <=2.6) and Zope (=>2.10.9 or =<2.12.17),
with `PIL` and `virtualenv` installed.

Create a virtualenv and activate it, then set up a new Zope instance using
the python binary from the virtualenv::

    virtualenv path/for/zope/instance
    cd path/for/zope/instance
    . bin/activate
    python /path/to/zope210/bin/mkzopeinstance.py -d . -u admin:admin

Install some dependencies from our package server::

    easy_install http://naaya.eaudeweb.ro/eggshop/itools-0.20.6.tar.gz
    easy_install http://naaya.eaudeweb.ro/eggshop/naaya.flowplayer-1.0dev_r13372-py2.4.egg
    cd lib/python2.4/site-packages
    svn checkout http://svn.eionet.europa.eu/repositories/Naaya/trunk/Naaya/Third-Party%20Products/Captcha
    cd ../../..

Development mode
----------------
Check out and install the Naaya package in development mode::

    mkdir src
    svn checkout https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/Naaya/ src/Naaya
    cd src/Naaya && python setup.py develop && cd ../..

This should have installed 3 extra packages which are actually bundled with
Zope2, so we need to remove the new ones. Edit the file
``lib/python2.4/site-packages/easy-install.pth`` and remove the following
lines::

    ./zope.component-3.8.0-py2.4.egg
    ./zope.interface-3.5.3-py2.4-linux-x86_64.egg
    ./zope.event-3.4.1-py2.4.egg

Install some additional Zope products::

    cd Products
    curl http://naaya.eaudeweb.ro/products/third-party/Localizer-1.2.2.tar.gz | tar xzf -
    mv Localizer-1.2.2 Localizer
    curl http://naaya.eaudeweb.ro/products/third-party/ExtFile-2.0.2.tar.gz | tar xzf -
    svn checkout http://svn.eionet.europa.eu/repositories/Naaya/branches/naaya2zope210/Third-Party/LocalFS
    cd ..

Add Naaya to Zope's configuration::

    echo '<include package="naaya.content.base" file="meta.zcml" />' \
        > etc/package-includes/Naaya-meta.zcml
    echo '<configure>
      <include package="naaya.content.base" />
      <include package="naaya.content.contact" />
      <include package="naaya.content.document" />
      <include package="naaya.content.event" />
      <include package="naaya.content.exfile" />
      <include package="naaya.content.file" />
      <include package="naaya.content.geopoint" />
      <include package="naaya.content.mediafile" />
      <include package="naaya.content.news" />
      <include package="naaya.content.pointer" />
      <include package="naaya.content.story" />
      <include package="naaya.content.url" />
      <include package="Products.TextIndexNG3" />
    </configure>' \
        > etc/package-includes/Naaya-configure.zcml

Now you should be able to start Zope and create a new instance of Naaya::

    zopectl fg

.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
