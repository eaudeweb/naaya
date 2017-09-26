CIRCA import
============

This is a small utility package that helps with migrating CIRCA interest
groups to Naaya.

Installation
------------
For `buildout`, make sure ``edw.circaimport`` is listed in the Zope
instance's ``eggs`` section. You need to check out the source code and
use it in development mode since no pre-built package is provided.

Create a file named ``circaimport.py`` in the Zope instance's
``Extensions`` folder with the following content, replacing
``/path/to/zip/files`` with the path to a local `CIRCA data folder` (see
below)::

    from edw.circaimport import work_in_zope
    def do_import(self, REQUEST):
        name = REQUEST.get('name')
        prefix = '/path/to/zip/files'
        return work_in_zope(self, name, prefix)

From the ZMI create an `external method` object. Use ``.circaimport``
for the id, ``circaimport`` for the module name and ``do_import`` for
the function name.


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
