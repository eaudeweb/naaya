.. py:currentmodule:: Products.naayaUpdater

Naaya Updater
=============

Sometimes simply updating the version of your Naaya code is not enough. Naaya
updates are procedures that apply updates to the content of your running portals
in a fast and controlled way.

Other updates represent quick ways of doing advanced operations to all
of your portals (e.g. updating translations, altering css rules).

If you have `naaya.updater` egg installed, you should see `naaya.updates` in
your Zope root. There you can visualize the list of the available updates
grouped by products. Each update consists in a form with a list of portals
available in your Zope instance. Simply check the portals
you want to be patched. You have the possibility to first perform a `Dry run`
with absolutely no changes.

Every event in the update procedure is logged.
