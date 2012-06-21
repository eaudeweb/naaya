CIRCA import
============

This is a small utility package that helps with migrating CIRCA interest
groups to Naaya (EIONET Forum - Groupware setup).

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

Also add a Zope environment variable called CIRCA_CIRCLE_NAME with the
circa group name (e.g. 'eionet-circle' for EIONET, 'circa-it' for
Italian CIRCA).


Folders migration
-----------------
You manually export folders from CIRCA using the "save" button. The "download"
button, next to it, does not save enough information. This produces a file
named ``download.zip``. Give it a more appropriate name and move it to the
folder you specified above in ZCML.

When the Zip files are ready, open the Naaya website, navigate to a
folder where you want to import the files (say ``my/import/folder``) and
access the url ``/import_from_circa_html`` in that folder::

    http://forum.eionet.europa.eu/my/import/folder/import_from_circa_html

Roles migration
---------------
You manually export roles from CIRCA using the "IG save" method. This generates
an archive (e.g. ``eea-eval.tgz`` or ``cca.tgz``). Move the file to the folder
you specified above in ZCML.

When the archives are ready, open the forum website and navigate to the IG
where you want to import the roles and access the URL
``/import_roles_from_circa`` in that IG::

    http://forum.eionet.europa.eu/my/import/IG/import_roles_from_circa

You can also manually extract the ``.ldif`` file in the same folder (the one
specified above in the ZCML) and import it the same way.

When importing the roles you need to specify the LDAP source title. This is the
source where the import script will search the users. The has to be available
in that IG (in ``Users management`` page from the administration). The title
of every source is shown in the ``Users management`` page (e.g. the tab name
for each source is ``%%source_title%% USERS``)

Notifications migration
-----------------------
You need to be able to login to dodo as circa21 to be able to export the
notification information. The Berkley DB files (version 3.x - internally called
version 5) are kept per interest group, e.g. for the ``scp`` IG::

    /opt/circa21/www/data/eionet-circle/scp/library/

Both ``usernotification.db`` and ``itemnotification.db`` contain the information,
but we use the 'usernotification.db'. You need to copy it to a workarea.

Logged in as circa21 you need to run the ``/opt/circa21/bin/db2gdbm.pl`` script
on the ``usernotification.db``. It will convert it to GDBM. Then you need to
run the ``gdbm_extract.py`` script on the ``usernotification.gdbm`` file.
You can find the script in the home directory of circa21 or in the
``edw.circaimport`` in svn (not all python versions/installations support GDBM).

Move the ``.csv`` file to the folder you specified above in ZCML.

When the archives are ready, open the forum website and navigate to the IG
where you want to import the roles and access the URL
``/import_roles_from_circa`` in that IG::

    http://forum.eionet.europa.eu/my/import/IG/import_notifications_from_circa

ACLs migration
--------------
You need to be able to login to dodo as circa21 to be able to export the ACL
information. The Berkley DB files are kept per interest group, e.g. for the
``nfp-eionet`` IG::

    /opt/circa21/www/data/eionet-circle/nfp-eionet/library/

Both ``useracls.db`` and ``itemsacls.db`` countain the information, but we use
only the ``itemsacls.db``. Copy it to a workarea.

Logged in as circa21 you need to run the ``/usr/local/bin/circadbprint`` script
on the ``itemsacls.db`` and redirect the output to a file
(e.g. ``itemsacls.txt``).

Move this file to the folder you specified above in ZCML.

When the files are ready, open the forum website and navigate to the IG where
you want to import the ACLs and access the URL
``/import_acls_from_circa`` in that IG::

    http://forum.eionet.europa.eu/my/import/IG/import_acls_from_circa
