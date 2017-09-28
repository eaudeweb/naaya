naaya.i18n Programmer's Guide
=============================

A complete internationalization API is available on the portal i18n object
in your portal.

>>> portal_i18n = portal.getPortalI18n()
>>> portal_i18n
<NaayaI18n at /portal/portal_i18n>
>>> portal_i18n.get_default_language()
'en'

Common operations in Python logic
---------------------------------

>>> portal_i18n.get_selected_language()
'en'
>>> portal_i18n.get_translation(u'Saved (${date})', date='19.07.2011 17:15')
u'Saved (19.07.2011 17:15)'
>>> portal_i18n.get_default_language()
'nl'
>>> portal_i18n.get_language_name('nl')
'Dutch'
>>> portal_i18n.get_languages_mapping()
[{'code': 'nl', 'name': 'Dutch'}, {'code': 'en', 'name': 'English'}]

Please read the complete available interface in :doc:`api/portal_tool`.

Translation in templates
-------------------------
The best way to do this is by using i18n:translate mark-up.
However, you can access the public interface of portal_i18n in TAL expressions:

* define your portal in a tal:block, e.g. `portal here/getSite`
* define the i18n tool: `portal_i18n portal/getPortalI18n`
* you now have access to its members: `tal:content="python:portal_i18n.get_translation('Click me')"`

Migrating from a Naaya that uses Localizer
------------------------------------------
These are the steps of migrating from Localizer to naaya.i18n:

* Back-up your Data.fs if you wish to
* Add edw-localizer and itools in buildout, eggs section
* Update naaya.updater code in develop. Add it if missing from your buildout
* Update your Naaya code, if installed in develop
* Run buildout
* Start Zope and access root/naayaUpdater in ZMI
* Run naaya.i18n migration update script for all of your portals
* Stop Zope daemon, remove itools and edw-localizer from buildout and re-run it
