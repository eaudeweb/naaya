Advanced operations
===================

Deleting a language
-------------------
The same Zope Management Interface you used for adding a language provides
the option of deleting one of the available languages. All the translations
in the deleted language will be kept in database for future use,
if you ever plan to put back the deleted language, but neither you nor the user
will have access to them.

Resetting internationalization
------------------------------
If something really wrong ever comes up, you can choose to do a full reset
of naaya.i18n: simply delete portal_i18n from Zope Management Interface
of your portal and re-add it from top right menu, `Naaya I18n`.

Every setting you made will be lost: available languages and
messages translations. Your objects will continue to keep their translations
in database.

Migrating from a Naaya using Localizer
--------------------------------------
If you are currently running a Naaya that uses Localizer for
internationalization, than you can use our update script to migrate your
translations. You need to update Naaya and naaya.updater and run
the update script in naayaUpdater under naaya.i18n heading. More details
are available in Programmer's Guide.

Moving objects and their translations to another portal
-------------------------------------------------------
You should be able to cut/copy content objects from another portal or import
them from a zexp file. The only condition for the data to work is
that both portals use naaya.i18n.
