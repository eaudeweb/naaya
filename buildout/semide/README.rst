SEMIDE Buildout
---------------

This package is designed to help you install Naaya and its dependencies,
including Zope. It makes use of the Buildout toolkit
(http://pypi.python.org/pypi/zc.buildout) and some of Plone's buildout recipes.

Read more:

https://svn.eionet.europa.eu/repositories/Naaya/buildout/Naaya/trunk/README.rst


SEMIDE
------

SEMIDE is build around Naaya CMS as a custom layer.


SEMIDE Deployment instructions
------------------------------

There are 2 types of possible deployments::
    * Production/development (a single zope-instance) - semide.cfg
    * Production ZEO (2 or more zope-instances with ZEO + pound) - semide-zeo.cfg

ZEO deployment may require some more configuration (setting up apache and pound)


Before you download and install python you need to have the following
dependencies first:

    build-essential (Required to compile python)
    zlib1g-dev (Used for zip support)
    libreadline-dev (Optional: useful for debugging purposes)
    libxslt-dev (Required by lxml)
    libmysqlclient-dev
    libsqlite3-dev


On Ubuntu or Debian install the dependencies with the following command

    sudo apt-get install build-essential zlib1g-dev libglib2.0-dev libreadline-dev libxslt-dev libmysqlclient-dev libsqlite3-dev


NOTE: If your already have Python-2.4.x and virtualenv skip the following 2 steps

1. Download and install Python-2.4.6 (http://www.python.org/ftp/python/2.4.6/Python-2.4.6.tgz).


2. Install virtualenv with the following command:

    pip install virtualenv


3. Checkout the SEMIDE buildout from https://svn.eionet.europa.eu/repositories/Naaya/buildout/semide/

    svn co https://svn.eionet.europa.eu/repositories/Naaya/buildout/semide/


4. Create and activate a virtualenv for Python 2.4 (http://pypi.python.org/pypi/virtualenv) in semide directory:

    virtualenv --python=</path/to/python/bin/python2.4> --no-site-packages --distribute .
    
    source bin/activate


6. Run bootstrap:
    #It is recommended to use virtualenv so that the deployement has a contained enviroment
    python bootstrap.py -c <semide-*>.cfg


7. Run buildout:

    bin/buildout -c <semide-*>.cfg


8. Start:

    #If you selected the production enviroment or development simply:
    bin/zope-instance start

    #If you selected zeo you need to start zeo server before any zope instances
    bin/zeo-server start
    bin/zope-instance1 start
    bin/zope-instance2 start
    ...
