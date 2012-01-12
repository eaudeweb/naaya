2.12.47 (unreleased)
--------------------

2.12.46 (2012-01-12)
--------------------
* added 'styleselect' in config.ini of portal editor,
removed from python code [simiamih]
* left/rightLogoUrl tests logo for empty file [simiamih]

2.12.45 (2012-01-11)
--------------------
* mailto links in in admin_bulk_email_html [dumitval]

2.12.44 (2012-01-09)
--------------------
* updated bundle migration script for groupware sites [dumitval]
* replace_illegal_xml for stripping xml-illegal characters [dumitval]

2.12.43 (2012-01-06)
--------------------
* template fixes for admin views topcontent and network [simiamih]

2.12.42 (2012-01-05)
--------------------
* UnicodeDecodeError in portal portlets [nituacor]

2.12.41 (2012-01-04)
--------------------
* The title of local channels is now utf8:ustring [dumitval]
* verify_html turned off for TinyMCE [andredor]
* fix non-ascii characters in subtitles [andredor]
* added missing gif loader from jquery-ui [simiamih]

2.12.40 (2011-12-20)
--------------------
* bugfix: glossary widget js now works on IE [simiamih]

2.12.39 (2011-12-19)
--------------------
* functionality to get users by email [andredor]

2.12.38 (2011-12-16)
--------------------
* geocoding address in csv import - reverted r17586 [simiamih]

2.12.37 (2011-12-16)
--------------------
* user photos for Users management (from LDAP cache) [andredor]
* `get_standard_template` fallback if macro not found [moregale]

2.12.36 (2011-12-15)
--------------------
* NyContentData.prop_exists [simiamih]

2.12.35 (2011-12-07)
--------------------
* dump errors to json file [andredor]
* content type factories (addNyContact ..)  return object when referer
  not the one expected [simiamih]

2.12.34 (2011-12-06)
--------------------
* added NyGadflyContainer for NaayaForum update [andredor]
* Added two methods in support of showing mainsection images [dumitval]
* Removed 'source' column from news and story folder indexes [dumitval]

2.12.33 (2011-11-29)
--------------------
* update script for migrating ew sites to bundles [andredor]
* change credentials page [andredor]
* fix for importing zip archives with filenames in non-ASCII [dumitval]
* get method in SyndicationTool [dumitval]
* fix acl_users/manage page [andredor]
* fix for empty string passed in geo_types filtering [dumitval]

2.12.32 (2011-11-18)
--------------------
* bugfix: standard error page and SchemaTool [simiamih]
* migrate StringWidget to URLWidget where needed [andredor]
* added docx, xlsx and pptx mime types [dumitval]
* gl_changeLanguage properly redirects when no referer [simiamih]

2.12.31 (2011-11-17)
--------------------
* portal_map methods are no longer called if the content type is not
  geo_enabled [dumitval]

2.12.30 (2011-11-16)
--------------------
* fix non empty titles for syndication [andredor]

2.12.29 (2011-11-16)
--------------------
* non empty titles for syndication [andredor]

2.12.28 (2011-11-16)
--------------------
* Bugfix related to uninstalled pluggable items [dumitval]

2.12.27 (2011-11-14)
--------------------
* permission information update [andredor]

2.12.26 (2011-11-11)
--------------------
* tinymce updated from 3.2.7 to 3.4.7 [simiamih]

2.12.25 (2011-11-10)
--------------------
* Inline documentation for portal metadata fields
* Information boxes for special roles in admin [andredor]
* Improved style for map balloon [bogdatan]
* removed broken obsolete getSymbolZPicture [simiamih]
* sitemap icon fix [andredor]

2.12.24 (2011-11-09)
--------------------
* revoke searched roles button for User management [andredor]

2.12.23 (2011-11-09)
--------------------
* location filter for User management search [andredor]
* option to disable openlayers map zoom with mouse wheel [moregale]
* view/add/revoke roles for user edit page (admin) [andredor]

2.12.22 (2011-11-08)
--------------------
* index_atom now shows also folders [dumitval]
* Improvements in adding and updating location categories [dumitval]
* Added Cut/Copy/Paste buttons to event, news and story folders [dumitval]
* One-click topstory setting for news and stories [dumitval]
* filter display for User management search [andredor]

2.12.21 (2011-11-04)
--------------------
* fix role filter in users management [andredor]
* Fix the `geo_query` map filter for non-English portals [moregale]
* When rendering error pages don't use the standard template [moregale]

2.12.20 (2011-11-04)
--------------------
* update script to fix local_channel non unicode attributes [andredor]

2.12.19 (2011-11-02)
--------------------
* remove ajax calls for Users' management [andredor]
* use second level tab for "Add new user" in Users' management [andredor]
* openlayers geocoding using google api [moregale]
* feature: admin can now assign roles in subsites #685 [simiamih]

2.12.18 (2011-10-31)
--------------------
* move sitemap_xml to Naaya forms [nituacor]

2.12.17 (2011-10-31)
--------------------
* fix translations in TinyMCE image selection pages [andredor]

2.12.16 (2011-10-31)
--------------------
* saveProperties for GlossaryWidget can save display and separator [andredor]

2.12.15 (2011-10-31)
--------------------
* removed googletranslate (also from languages_box.zpt) [dumitval]
* remove link checker from cron heartbeat [moregale]

2.12.14 (2011-10-28)
--------------------
* current unapproved items restricted for view [andredor]

2.12.13 (2011-10-28)
--------------------
* Owner can have just edit content permission (admin other properties) [andredor]
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
