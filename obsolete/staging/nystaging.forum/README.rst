Staging tests package for forum.eionet.europa.eu
===================================================

1. This package contains staging tests for a production version of 
   forum.eionet.europa.eu.
2. Using functional ui tests (selenium) it will test each portal for possible
   failures.
3. These tests are intended to be run using `nose` test runner.
4. These package should be used inside a buildout environment.

Installation
--------------

1. Buildout configuration
+++++++++++++++++++++++++++++

Put the following section in your ``buildout.cfg`` under ``naaya-nose`` section::

[naaya-nose]
eggs = #Add to eggs
    nystaging-forum

Run ``buildout``.

Usage
-------------

Run::

    ./bin/nynose --nodemo /path/to/nystaging-forum

This will run a nose without demostorage (it will use the real database)
