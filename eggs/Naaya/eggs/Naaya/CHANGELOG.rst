2.12.13 (unreleased)
--------------------
* removed site logo versions for all portal languages [dumitval]
* unapproved items restricted for view [andredor]
* no google analytics tracking for managers [andredor]
* recover password email for more accounts with same email [andredor]
* Hide contributor and releasedate for anonymous users [nituacor]
* Create map symbols based on skel.xml [moregale]
* checkboxes for legend filters, callback for refresh_points in map [simiamih]

2.12.12 (2011-10-24)
--------------------
* remove old captcha tool [andredor]
* using reCAPTCHA for add and feedback forms [andredor]
* warning message if reCAPTCHA not present [andredor]
* fix 'geo-tagged' disabled for Folders (#717) [andredor]
* added update for changing user roles (specific for CHM_NL) [dumitval]
* portal_map URL hash updated with current selection [moregale]
* portal_map js and css fixes for IE 7-9 [simiamih]

2.12.11 (2011-10-19)
--------------------
* removed Glossaries tab from admin portal properties [dumitval]
* removed Properties tab for the site (#710) [andredor]

2.12.10 (2011-10-19)
--------------------
* portal_map redesign - cleaner legend, no checkboxes, less elements [simiamih]

2.12.9 (2011-10-18)
-------------------
* fix basket of approvals redirect [andredor]

2.12.8 (2011-10-17)
-------------------
* view permission not inherited for new sites [andredor]
* fix copy/cut/paste/delete redirect for top objects [andredor]

2.12.7 (2011-10-14)
-------------------
* admin top content page [andredor]
* main topics admin page doesn't add/delete folders [andredor]
* portlet administration on disk for new semide sites [andredor]
* portlet administration also on disk [andredor]

2.12.6 (2011-10-13)
-------------------
* Fix TypeError in latestcomments_rdf: syndicateThis() takes exactly 2 arguments (1 given) [nituacor]
* Event, news, stories and folder listing improvements [dumitval]
* Fix news and stories folder sort order [andredor]
* Zip download link is no longer shown if there are no objects to download
  [dumitval]
* OpenLayers map engine [moregale]
* Simple map markers generated based on a color [moregale]

2.12.5 (2011-10-11)
-------------------
* Bundle names based on full site path [andredor]

2.12.4 (2011-10-11)
-------------------
* Style fix for indexes without right portlets [dumitval]

2.12.3 (2011-10-11)
-------------------
* Sites are no longer considered container meta-types [simiamih]

2.12.2 (2011-10-10)
-------------------
* Removed duplicate right portlets from the story and news custom templates
  [dumitval]

2.12.1 (2011-10-10)
-------------------
* Added NaayaPageTemplates for News and Stories custom folders [dumitval]
* Moved content rating and folder social icons to top, fixed stykes [bogdatan]
* Set focus on the username field on load [dumitval]

2.12.0 (2011-10-06)
-------------------
* refactor: :mod:`Products.Naaya.NySite` stores Zope and
  Naaya containers meta_type-s in two lists in the beginning of the module
* refactor: :mod:`naaya.i18n` replaces Localizer and itools
* refactor: :mod:`Products.NaayaCore.FormsTool` templates registered via ZCA
  and bundles [plugaale, andredor, moregale]
  update script: "Migrate to bundles"
* Bundles inspector [andredor, plugaale]
* Move customized templates from ZODB to filesystem bundles [moregale]

2.11.5 (2011-09-23)
--------------------
* New release for CHM server migration to use the eggshop (no more svn)

2.11.3 (2011-04-07)
--------------------
* Folder listing fetches all information about listed objects using adapters.
* Fix: ``naaya.core.zope2util.permission_add_role`` used to incorrectly toggle
  the permission.
* Fix: Zip export used to leave out extensions if filename already contained
  a dot.
* Remove all license headers and a lot of uneeded files (e.g. empty readmes).
* Roles editing is protected with the permission `Change permissons`.
* Fix: "Exception while rendering an error message".
* Clean up NotificationTool. Subscribers now receive emails on zip/csv import.
* Zip download now includes URLs as well.
* Naaya sites have a `LocalSiteManager`.
* `ActionLogger` remembers events in ZODB. Each site has one.
* New widget type, `IntervalWidget`.
* `NotificationTool` saves edit events in the action logger.
* Notifications can be disabled temporarily by admins for their own edits.
* New `GlossaryWidget` with jquery-ui.

2.11.2 (2011-03-01)
--------------------
* New permission `Naaya - Skip approval` replaces `submit_unapproved` flag.
  `checkPermissionSkipApproval` replaces `glCheckPermissionPublishObjects`.
* Content objects have new `deleteThis` method with permission
  `Naaya - Delete objects`.
* Improvements to Zip import and export: title/id mapping, preservation of
  timestamps, keeping empty folders.
* Usability improvements to notifications administration page.
* Separate email addresses for admin notifications and error reports.


2.11.1 (2011-02-02)
--------------------
* Support for i18n messages with different values for ID and English
   translation, useful for handling homonyms.


2.10.12 (2011-01-11)
--------------------
* Zip export uses temporary file instead of building archive in memory.
* Feature: anonymous subscriptions to notifications. Improvements to
  subscriptions UI.
* Refactoring of custom index_html template for folders.
* New paginator for naaya: used in site_search and notification admin.
* CSV import of user accounts.

2.10.11 (2010-12-07)
--------------------
* Map info balloons no longer require a catalog search; they are requested
  based on visible markeres on the map.
* Load information for LDAP users from a cache, if available. The cache is
  created by the ``naaya.ldapdump`` package.
* Fix: Users with `View` privileges in a sub-folder but not at site level no
  longer receive `Unauthorized` errors.
* Fix: many issues with site search.
* Selenium testing harness refactoring; can use CherryPy instead of wsgiref.
* Feature: customize template for each Schema Widget instance.

2.10.10 (2010-11-04)
--------------------
* ProfilesTool refactored to subclass from BTreeFolder2. Update script:
  `Change ProfilesTool to use BTree`.
* ProfilesTool moved from NaayaCore to Products.NaayaProfilesTool because it
  is rarely used and shouldn't be in the Core
* Major UI update for Products.NaayaCore.AuthenticationTool. Using ajax
  in user management (administration), fixed a lot of bugs and improved LDAP
  performance.
* Fix: NotificationTool subscriptions - strip user_id spaces. The update
  script `Remove spaces from ...` will remove existing spaces.
* Feature: user password reset with email verification
* Fix: templates customized in ``portal_forms`` now accept ``**kwargs``
* Refactoring for code that walks a `RefTree`
* Improvements to DiskFile object; new DiskTemplate object; can be added
  from ``skel.xml``.
* Meta tags for all content types (index pages). Includes: `description`,
  `keywords`, `contributor`, `dc.language` and `title`
* Permissions editor: shows acquired permissions; fix locating target object
* Comments refactored to store information in a hidden folder. Update script:
  `Migration script from Naaya Comments`.

2.10.9 (2010-10-06)
-------------------
* First numbered version
