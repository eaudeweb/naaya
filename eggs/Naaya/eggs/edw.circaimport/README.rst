CIRCA import
============

This is a small utility package that helps with migrating CIRCA interest
groups to Naaya.

Installation
------------
For `buildout`, make sure ``edw.circaimport`` is listed in the Zope
instance's ``eggs`` section. You need to check out the source code and
use it in development mode since no pre-built package is provided. Make
sure to include the ``edw.circaimport`` and ``edw.circaimport-meta`` ZCML
files.

Add a ZCML configuration entry to specify where CIRCA Zip files will be found
(see "Usage" below). Example::

  zcml =
    edw.circaimport
    edw.circaimport-meta
  zcml-additional =
    <configure xmlns:circaimport="http://xmlns.eaudeweb.ro/edw.circaimport">
        <circaimport:root path="${buildout:directory}/var/circaimport"/>
    </configure>


Usage
-----
You manually export folders from CIRCA using the "save" option. This
produces files named ``download.zip``. Give them more appropriate names
and move them to a folder (referred to as `CIRCA data folder` above) on
the same machine as the Naaya site.

When the Zip files are ready, open the Naaya website, navigate to a
folder where you want to import the files (say ``my/import/folder``) and
run the external method *in the context of that folder*. It takes a
`name` parameter, the name of the Zip file to import::

    http://my.naaya.portal/my/import/folder/.circaimport?name=thedocs.zip
