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
    <configure xmlns:circaimport="http://ns.eaudeweb.ro/edw.circaimport">
        <circaimport:root path="${buildout:directory}/var/circaimport"/>
    </configure>


Usage
-----
You manually export folders from CIRCA using the "save" button. The "download"
button, next to it, does not save enough information. This produces a file
named ``download.zip``. Give it a more appropriate name and move it to the
folder you specified above in ZCML.

When the Zip files are ready, open the Naaya website, navigate to a
folder where you want to import the files (say ``my/import/folder``) and
access the url ``/import_from_circa_html`` in that folder::

    http://forum.eionet.europa.eu/my/import/folder/import_from_circa_html
