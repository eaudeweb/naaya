4.0.25 (unreleased)
-------------------
* typo fix in skel.xml [dumitval]
* improvement in make_id [dumitval]

4.0.24 (2015-11-12)
-------------------
* improvement in make_id [dumitval]

4.0.23 (2015-11-10)
-------------------
* bugfix in admin page of notifications [dumitval]

4.0.22 (2015-11-06)
-------------------
* fix in editor tool insert image [dumitval]

4.0.21 (2015-10-29)
-------------------
* added language packs for tinymce [dumitval]

4.0.20 (2015-10-26)
-------------------
* updated skel permissions for use in reset role [dumitval]

4.0.19 (2015-10-23)
-------------------
* fix url_quote crash for unicode properties [dumitval]
* select image from current portal brought back to Editor Tool [dumitval]

4.0.18 (2015-10-22)
-------------------
* bugfix related to showing glossary elements in portal editor tree
  [dumitval]

4.0.17 (2015-10-22)
-------------------
* bugfix related to showing glossary elements in portal editor tree
  [dumitval]

4.0.16 (2015-10-21)
-------------------
* updated tinymce to v. 3.5.11 to fix IE insert link bug [dumitval]

4.0.15 (2015-10-20)
-------------------
* show glossary and its elements in portal editor link creator [dumitval]

4.0.14 (2015-10-19)
-------------------
* mediafile: skip encoding for compliant audio and mp4 max 720p [dumitval]
* mediafile: show "still encoding" message, catch encodding error message [dumitval]
* mediafile: fix for file upload on IE [dumitval]

4.0.13 (2015-10-16)
-------------------
* mediafile fix for mp3 files [dumitval]

4.0.12 (2015-10-16)
-------------------
* change libfaac to libfdk_aac for audio encoding [dumitval]

4.0.11 (2015-10-15)
-------------------
* upgrade mediafile to HTML5 (mp4 file encoding, flowplayer 6.0.3) [dumitval]
* cosmetic improvement on admin_contenttypes page [dumitval]

4.0.10 (2015-10-01)
-------------------
* fix in plugLDAPUserFolder.py [dumitval]

4.0.9 (2015-09-30)
-------------------
* updated datatables to 1.10.9 [dumitval]
* removed further references to disabled@eionet.europa.eu [dumitval]

4.0.8 (2015-09-15)
-------------------
* filter out disabled users from search results [dumitval]

4.0.7 (2015-09-14)
-------------------
* add email in listUsersInGroup results info [dumitval]

4.0.6 (2015-08-04)
-------------------
* Bug fix: fix sending emails on non-EEA websites
  [tiberich]

4.0.5 (2015-06-25)
-------------------
* bugfix in excel encoding processing [dumitval]

4.0.4 (2015-06-23)
-------------------
* bugfix in findUsers [dumitval]

4.0.3 (2015-06-22)
-------------------
* Bug fix: set as unicode disabled email address, needed by AuthenticationTool
  [tiberich #26781]

4.0.2 (2015-06-19)
-------------------
* changed utils sort function to check lowercase [dumitval

4.0.1 (2015-05-28)
-------------------
* moved AuthenticationTool utils from meeting [dumitval]

4.0 (2015-05-18)
-------------------
* improved the logic in mail archive checking [dumitval]

3.4.24 (2015-05-07)
-------------------
* add only_to and only_cc parameters to send email [dumitval]

3.4.23 (2015-04-09)
-------------------
* Moved the extended filters before the search results (site_search)
  [dumitval]
* added a configuration setting to datatables on site_search to keep
  search settings when returning to the table with the browser's back
  button [dumitval]

3.4.22 (2015-04-08)
-------------------
* escape title portal editor/insert image [dumitval]

3.4.21 (2015-04-07)
-------------------
* added utils method to import non-local libraries [dumitval]

3.4.20 (2015-03-31)
-------------------
* fixes for the manage_folder_subobjects page [dumital]

3.4.19 (2015-03-30)
-------------------
* fixes for the manage_folder_subobjects page [dumitval]

3.4.18 (2015-03-30)
-------------------
* updated Naaya local users listing to work with datatables (no merged
  cells) [dumitval]

3.4.17 (2015-03-27)
-------------------
* update make_id to strip unwanted leading and trailing characters from
  the id [dumitval]

3.4.16 (2015-03-19)
-------------------
* corrected the class on the recaptcha error message [dumitval]

3.4.15 (2015-03-12)
-------------------
* reCaptcha 2.0 compatibility [dumitval]

3.4.14 (2015-03-05)
-------------------
* hide external users with no valid roles from all users listing [dumitval]

3.4.13 (2015-02-27)
-------------------
* search results table is now powered by dataTables [dumitval]
* Added upload date column to the site search results (files only)
  [dumitval]

3.4.12 (2015-02-24)
-------------------
* move object_index_map to NaayaPageTemplate [dumitval]

3.4.11 (2015-02-18)
-------------------
* Change: keep the Owner roles when restricting access to a folder
  [tiberich #19452]
* Bug fix: remove version from google map externally loaded JS, it was causing
  issues with the portal map
  [tiberich]

3.4.10 (2014-12-10)
-------------------
* increase size of eionet group imput [dumitval]

3.4.9 (2014-12-10)
-------------------
* bugfix in adding short name objects ('and', 'for', 'at', etc.) [dumitval]
* option to replace existing files when uploading from zip [dumitval]

3.4.8 (2014-12-09)
-------------------
* fix for import from zip with improperly encoded zip file [dumitval]
* Bug fix: fix "RESTRICTED ACCESS" string rendering in map baloon
  when access is restricted
  [tiberich]

3.4.7 (2014-11-26)
-------------------
* Bug fix: fix resolution detection on MPG streams
  [tiberich]
* Bug fix: fix sending notification emails
  [tiberich]

3.4.6 (2014-11-25)
-------------------
* upcoming_events portlet fix for meeting objects [dumitval]
* Bug fix: fix media convertor availability check
  [tiberich]

3.4.5 (2014-11-21)
-------------------
* Bug fix: avoid problem with un-migrated Publications
  [tiberich #3929]

3.4.4 (2014-11-14)
-------------------
* don't delete ga_id on access revoke [dumitval]
* skip notifications for disabled users [dumitval]

3.4.3 (2014-11-06)
-------------------
* removed requests from backport, properly imported now [dumitval]
* log adding of roles [dumitval]

3.4.2 (2014-10-30)
-------------------
* Bug fix: backward compatibility with extfiles not migrated:
  if filename is string, return it, instead of last item
  [tiberich #3929]
* Bug fix: avoid error in datatables when user has multiple roles
  [tiberich #21517]

3.4.1 (2014-10-28)
-------------------
* import from zip: handle non-zip upload wihout site error [dumitval]
* Bug fix: make NyFSFile use blobfiles instead of extfiles
  [tiberich #3929]

3.4.0 (2014-10-09)
-------------------
* Feature: merge with the no-ext-files branch that implements
  blob files for storage of files
  [tiberich #3929]
* Bug fix: fix bug with zooming of google engine portal map
  [tiberich]

3.3.67 (2014-10-06)
-------------------
* removed users bulk download from the interface [dumitval]
* all tables in user administration are now dataTables [dumitval]

3.3.66 (2014-09-12)
-------------------
* bugfix in mediafile commandline encoding [dumitval]

3.3.65 (2014-09-11)
-------------------
* mediafile keeps video size when encoding [dumitval]
* Avoid throwing error when getting full username for user when retrieving
  user info from old ldap cache
  [tiberich #20725]

3.3.64 (2014-08-11)
-------------------
* error handling when a user doesn't have a status (admin_users_html)
  [dumitval]

3.3.63 (2014-08-08)
-------------------
* UnicodeDecodeError fix notifications for roles with non-ASCII chars
  [dumitval]

3.3.62 (2014-08-06)
-------------------
* Feature: show disabled status of users in the "Eionet users" management tab;
  allow filters by disabled status, in the "All users" tab of the "Users management"
  page
  [tiberich #20390]

3.3.61 (2014-07-31)
-------------------
* bugfix related to my_notifications for LDAP portals [dumitval]

3.3.60 (2014-07-29)
-------------------
* Message in my_notifications page for users defined at a higher
  hierarchical level [dumitval]

3.3.59 (2014-07-28)
-------------------
* bugfix in save_bulk_email [dumitval]
* added i18n tags to the cookie disclaimer message [dumitval]
* Change: remove code related to API key for google map engine
  [tiberich #15626]

3.3.58 (2014-07-08)
-------------------
* Bug fix: cleanup the source code of google map engine js. 
* Bug fix: fix go_to_address_with_zoom function of google map engine
  [tiberich #15626]

3.3.57 (2014-06-30)
-------------------
* ignore disabled@eionet.europa.eu as recipient for notifications [dumitval]

3.3.56 (2014-06-26)
-------------------
* handling for expirationdate set to None in some objects [dumitval]

3.3.55 (2014-06-25)
-------------------
* hide LocalChannel objects if they expired and don't have 'topitem' set
  [dumitval]

3.3.54 (2014-06-24)
-------------------
* hide rdf objects if they expired and don't have 'topitem' set [dumitval]

3.3.53 (2014-06-17)
-------------------
* bugfix in site_googleanalytics [dumitval]

3.3.52 (2014-06-06)
-------------------
* bugfix for the Notification system (UnicodeDecodeError) [dumitval]

3.3.51 (2014-06-05)
-------------------
* handle news and stories with missing properties (source, topitem) [dumitval]

3.3.50 (2014-05-26)
-------------------
* fix for the CC recipients issue [dumitval]
* fixed some tests after the change of default enable notifications [dumitval]

3.3.49 (2014-05-06)
-------------------
* jquery datatables on notification admin page [dumitval]
* Changed wording in the password reset form (Recover --> Reset) [dumitval]

3.3.48 (2014-04-17)
-------------------
* enabled ZIP64 extension [dumitval]

3.3.47 (2014-04-17)
-------------------
* re-added an import (SubscriptionContainer) for backwards-compatibility [dumitval]

3.3.46 (2014-04-08)
-------------------
* Changed wording in restrict_html [dumitval]

3.3.45 (2014-04-07)
-------------------
* Task #17799 - choose emails to export to xcel [baragdan]

3.3.44 (2014-04-04)
-------------------
* improvement for comments on removed versions [dumitval]

3.3.43 (2014-04-03)
-------------------
* update google_analytics snippet to use analytics.js [dumitval]

3.3.42 (2014-03-28)
-------------------
* refactor role assignment notifications  to use the notification tool [dumitval]
* send notification to user when his Administrator role has been revoked [dumitval]
* show external sources tab before local users (user admin) [dumitval]

3.3.41 (2014-03-13)
-------------------
* Enable all notification types on new IGs [dumitval]

3.3.40 (2014-03-11)
-------------------
* Fixed email templates typo (folowing) [dumitval]
* Fixed xcel typo [dumitval]
* Fixed problem with Python Google geocoder when trying to retrieve unicode addresses
  [tiberich]

3.3.39 (2014-03-05)
-------------------
* display comments paired with the document version (files) [dumitval]

3.3.38 (2014-02-26)
-------------------
* Bug fix: added an update script to remove the API key from portal geomap tool
  [tiberich]

3.3.37 (2014-02-20)
-------------------
* update script for portlets for folders (to display content) [dumitval]
* added "Naaya Meeting" to folderish metatypes [dumitval]

3.3.36 (2014-02-07)
-------------------
* get_objects_for_rdf returns objects where the user has view [dumitval]

3.3.35 (2014-01-31)
-------------------
* Show Meeting objects in roles-in-location listing [dumitval]
* change upcoming_events portlet to display event type [dumitval]
* Empty script channels don't crash anymore [dumitval]

3.3.34 (2014-01-22)
-------------------
* Bug fix: improve performance of security inspector
  [tiberich #18127]

3.3.33 (2014-01-21)
-------------------
* Use a monthly based file handler for logging the site logging activity
  This improves performance in the site logger viewer page.
  [tiberich #17131]

3.3.32 (2014-01-17)
-------------------
* Bug fix: make sure the over query limit error is raised when geocoding
  [tiberich]
* Bug fix: don't fail when going to the IG Logging page when there's no
  SITES_LOG_PATH env variable set
  [tiberich #17131]
* Bug fix: don't throw error when failing to parse a line in the JSON file
  Note: this should be regarded as catastrophic failure, there should be
  no real cause that the log file is not a valid JSON file
  [tiberich #17131]

3.3.31 (2014-01-16)
-------------------
* Bug fix: fix csv import when trying to geocode records and failing
  [tiberich]

3.3.30 (2014-01-15)
-------------------
* Fixed bug related to notification tool relative import
  [tiberich]

3.3.29 (2014-01-15)
-------------------
* Bug fix: fix direct email delivery when deployed with repoze.sendmail
  [tiberich #17998]
* Bug fix: fix google map setup code
  [tiberich]

3.3.28 (2014-01-14)
-------------------
* xlwt and xlrd added to Naaya as dependencies. No need to assert availability. [dumitval]
* Feature: use the Google Maps API v3, by merging the special branch
  [tiberich #16938]
* Bug fix: don't throw error when uploading an image with non-ascii chars
  [tiberich #17797]
* Feature: added the possibility to customize tinymce styles by adding
  a DTML Document called custom_css in the portal_editor.
  [tiberich #17451]

3.3.27 (2014-01-08)
-------------------
* Change: also show the username in the account modified email that is sent
  [tiberich #17642]

3.3.26 (2014-01-07)
-------------------
* task 17799 - export mail list to xcel [baragdan]
* EmailValidator - added validation attempts to repeat test for invalid addresses (avoid false negatives)
* updated some tests to work with the new cc field in diverted mail [dumitval]

3.3.25 (2013-12-18)
-------------------
* added some missing changes to the cc email functionality [dumitval]

3.3.24 (2013-12-18)
-------------------
* class-based selection of cells with emails to be validated [dumitval]
* getUserFullName returns "Anonymous User" for anonymous, instead of '' [dumitval]
* Feature: added a couple of methods to symbols_tool to improve API and ease migration of destinet contacts [tiberich #17642]

3.3.23 (2013-12-11)
-------------------
* Email Validation - resolve validation in backend threads (avoid server load) [baragdan]
* Bug fix: don't crash when offloading to disk bundles the templates that have
  non-ascii characters (unicode)
  [tiberich]

3.3.22 (2013-12-09)
-------------------
* Email Validation - controll js parallelism (avoid server load) [baragdan]
* Bug fix: don't override the base_layer in openlayers engine with the
  global defaults, the global default is just a string while the OpenLayer
  engine expects a mapping
  [tiberich #17700 Destinet]
* Bug fix: don't crash when a contact is found with no values filled in
  [tiberich #17643 Destinet]

3.3.21 (2013-12-05)
-------------------
* `update` Email address validation for syntax and existence [baragdan]
* Return address as strings in geocoding manager module
  [tiberich #16938]

3.3.20 (2013-11-29)
-------------------
* Updated naaya.core.ggeocoding to use GoogleMaps api v3
  [tiberich #16938]
* Updated GeoMapTool to use naaya.core.ggeocoding methods instead of
  reimplementing
  [tiberich #17553]
* Added a few missing methods to OpenLayers JS engine, to improve
  compatibility with older geomaptool.js file from Destinet.
  [tiberich #17553]

3.3.19 (2013-11-19)
-------------------
* _mail_in_queue moved to EmailTool [dumitval]

3.3.18 (2013-11-11)
-------------------
* added method to retrieve current mail_queue [dumitval]

3.3.17 (2013-11-06)
-------------------
* mark new users in admin_assignroles (except in EEA sites) [dumitval]
* fix for naaya.content.url DateTime parsing [dumitval]
* Changed latestuploads_rdf.zpt to sort reversed on last_modification [dumitval]

3.3.16 (2013-11-04)
-------------------
* script to update latestuploads.zpt portlet from skel [dumitval]

3.3.15 (2013-10-31)
-------------------
* Mandatory file upload in Naaya File [dumitval]

3.3.14 (2013-10-30)
-------------------
* Removed LDAP users from search results (assign role page) [dumitval]

3.3.13 (2013-10-15)
-------------------
* added get_ldap_user_groups method [dumitval]
* display 'discard version' also on the checked-out item's index [dumitval]

3.3.12 (2013-08-27)
-------------------
* fixes to zip_import so it works with unicode folder and file names [dumitval]

3.3.11 (2013-08-21)
-------------------
* reverted jquery to version 1.7.1 because of jstree issues [dumitval]

3.3.10 (2013-08-06)
-------------------
* changed default depth for tree objects [dumitval]

3.3.9 (2013-08-01)
-------------------
* fix for a notification tool crash with unicode names [dumitval]

3.3.8 (2013-07-26)
-------------------
* reverted an import cleanup, it seems it broke something [dumitval]
* removed old email templates and old method notifyMaintainerEmail [dumitval]

3.3.7 (2013-07-26)
-------------------
* nyexfile: notification only sent if there is a REQUEST [dumitval]
* updated jquery to version 1.7.2 [dumitval]
* updated jquery-ui to version 1.9.2 [dumitval]
* updated tests for notifications [dumitval]
* added notifications on comments (to owner, subscribers) [dumitval]
* updated default permissions [simiamih]

3.3.6 (2013-07-12)
-------------------
* feature: #14233 - reset default permissions for a role [simiamih]
* my_subscriptions_html: change legend (edit/new) accordingly [dumitval]

3.3.5 (2013-07-11)
-------------------
* Subscriptions editing improvements [dumitval]

3.3.4 (2013-07-11)
-------------------
* added possibility to edit existing subscriptions [dumitval]

3.3.3 (2013-07-10)
-------------------
* Fixed duplicate sending of administrative emails [dumitval]

3.3.2 (2013-07-10)
-------------------
* link from event index to contributor's user profile [dumitval]

3.3.1 (2013-07-10)
-------------------
* identify user source after lowering case [dumitval]

3.3.0 (2013-07-10)
-------------------
* #14873 email settings warnings [simiamih]
* `update` Introduced administrative notifications [dumitval]
* links to eionet user profiles from user administration and other pages [dumitval]
* subscribe to notifications by content type [dumitval]

3.2.39 (2013-05-24)
-------------------
* fix for the tree browser in link editor [dumitval]
* moved skipt captcha update script from naaya.groupware [dumitval]

3.2.38 (2013-05-22)
-------------------
* bugfix in recaptcha keys from buildout [dumitval]
* removed getFolderMaintainersEmails() - never used [mihaitab]

3.2.37 (2013-05-20)
-------------------
* template fix [dumitval]

3.2.36 (2013-05-20)
-------------------
* template fix [dumitval]

3.2.35 (2013-05-20)
-------------------
* set reCAPTCHA keys also in buildout [dumitval]

3.2.34 (2013-05-17)
-------------------
* add new permission for webex requests [mihaitab]

3.2.33 (2013-04-03)
-------------------
* bugfix in frameservice (in case of Anonymous) [dumitval]

3.2.32 (2013-04-03)
-------------------
* frameservice modification (groups are now independently searched) [dumitval]

3.2.31 (2013-03-26)
-------------------
* optional filters by meta_type added to Ajax tree [nituacor]
* narrow Zip import to .zip files only [mihaitab]

3.2.30 (2013-03-18)
-------------------
* inline styling for delete_confirmation [dumitval]
* #14158 frameservice provides user groups (eionet roles) [simiamih]
* #14093 fixed tipsy [simiamih]

3.2.29 (2013-03-15)
-------------------
* import_export change - inconsistent content will still export [dumitval]
* same slots for add and edit schema forms [simiamih]
* View for Reviewer [simiamih]

3.2.28 (2013-03-12)
-------------------
* changed Stard-End labels in interval widget [mihaitab]
* "Center map" button initially visible on map widget [dumitval]
* added change-ownership file in extra [mihaitab]
* restrictions on objects listing (reverted setting for folders) [dumitval]

3.2.27 (2013-03-07)
-------------------
* temp disabled of tipsy
* actual fix of change in 3.2.24 [simiamih]

3.2.26 (2013-03-07)
-------------------
* added siteurl in front of ++ressource (frameservice compatibility) [dumitval]

3.2.25 (2013-03-07)
-------------------
* restrictions on objects listing (view permission required) [dumitval]
* meaningful error message - column exceeds Excell cell size limit [mihaitab]

3.2.24 (2013-03-07)
-------------------
* use member_search in frameservice, if available [simiamih]

3.2.23 (2013-03-07)
-------------------
* bugfix in delete confirmation dialog, basketofapprovals [dumitval]

3.2.22 (2013-03-06)
-------------------
* first version that requires Zope 2.12 [simiamih]
* Delete confirmation dialog in basketofapprovals [dumitval]
* info message on startup with link of instance dev url [simiamih]

3.2.21 (2013-03-01)
-------------------
* last version supporting Zope 2.10 [simiamih]
* frameservice changes to return more data [dumitval]
* search fix for users from the notifications' admin page [mihaitab]

3.2.20 (2013-02-22)
-------------------
* js fix for time interval widget [simiamih]

3.2.19 (2013-02-15)
-------------------
* error handling in getLinksListById [dumitval]

3.2.18 (2013-02-13)
-------------------
* bugfix in multiple select widget [dumitval]

3.2.17 (2013-02-07)
-------------------
* added script channels to local ch. portlet administration page [dumitval]

3.2.16 (2013-02-05)
-------------------
* bugfix in restrict view and improved speed [simiamih]

3.2.15 (2013-01-31)
-------------------
* bugfix #13604: changed default placeholder [mihaitab]
* fine adjustments to access overview in restrict folder [simiamih]
* tipsy in site scripts, improved ig logger view [simiamih]
* bugfix #13604: HTMl document weird replace [mihaitab]
* bugfix #10266: Rename button for Contributors [mihaitab]
* Statistics: redirect to profile selection if no profile selected [dumitval]
* show Google client id and secret key in api key status [dumitval]

3.2.14 (2013-01-25)
-------------------
* ldap_cache: unsuccessful init update behaves as cache miss [simiamih]
* feature: restrict folder can be used to make folder public [simiamih]

3.2.13 (2013-01-11)
-------------------
* naaya.monitor zcml loaded if installed [simiamih]
* update email message in notifications by zip upload [mihaitab]
* *update* fix Google Analytics bugs; disallow changing the profile.
  Need to configure `GOOGLE_AUTH_CLIENT_ID` and
  `GOOGLE_AUTH_CLIENT_SECRET` environment variables. [moregale]

3.2.12 (2012-12-19)
-------------------
* eliminate redundant notifications sent by zip upload [mihaitab]

3.2.11 (2012-12-17)
-------------------
* yet another bugfix for Google Analytics API [moregale]

3.2.10 (2012-12-17)
-------------------
* bugfix for Google Analytics API [moregale]

3.2.9 (2012-12-17)
-------------------
* Add `gdata` dependency because of broken objects [moregale]
* *update* script: remove `gdata` object instances [moregale]

3.2.8 (2012-12-17)
-------------------
* Update access to Google Analytics API [moregale]

3.2.7 (2012-12-14)
-------------------
* GeoWidget map initially visible [dumitval]
* automatic geocoding where the address is available [dumitval]
* removed unnecessary change to html2text [dumitval]

3.2.6 (2012-12-13)
-------------------
* Bulk mail improvements [dumitval]

3.2.5 (2012-12-13)
-------------------
* notifications to subscribers are only sent in object-approved handler [mihaitab]
* pretty_path for NyContentType [simiamih]
* added tipsy tool-tip jquery plugin [simiamih]
* overview of access in restrict folder [simiamih]
* module for inspecting security settings [simiamih]
* choose base layer for OpenLayers map [moregale]

3.2.4 (2012-11-27)
-------------------
* new icon for NyFolder [simiamih]
* support for utf-8 LDAP encoding [simiamih]
* deprecated cn forever-cache on zodb [simiamih]
* save and display sent bulk emails [bogdatan, simiamih]
* new "initial zoom level" option for portal map [moregale]

3.2.3 (2012-11-20)
-------------------
* #10014 - List emails in Assign role to Users [mihaitab]

3.2.2 (2012-11-20)
-------------------
* made RESPONSE headers compatible with IE browsers [nituacor]

3.2.1 (2012-11-19)
-------------------
* naaya.cache is req to be 1.1 which works with Zope 2.10 [simiamih]
* bugfix: UnicodeEncodeError (LDAP encoding is now UTF-8) [nituacor]

3.2.0 (2012-11-16)
-------------------
* ldap groups: using naaya.cache instead of volatile attributes [simiamih]
* new dependency: naaya.cache [simiamih]

3.1.15 (2012-11-14)
-------------------
* bugfix #10017: DateWidget date conversion fix (import from file) [dumitval]

3.1.14 (2012-11-09)
-------------------
* bugfix: inheritance issues: move NyFolderBase after NyRoleManager [nituacor]

3.1.13 (2012-11-09)
-------------------
* bugfix: #9951; copy-cut-paste raised `Error while pasting data` for owners [nituacor]

3.1.12 (2012-11-08)
--------------------
* user photos are not restricted [simiamih]
* checkPermissionReview [simiamih]
* don't acquire `approved` attribute when updating it [moregale]

3.1.11 (2012-10-24)
--------------------
* *update* #1012 script for refreshing Google MAPS API Key [simiamih]
* new default API Key for Google maps engine [simiamih]

3.1.10 (2012-10-23)
--------------------
* added cookie disclaimer message + consent request [dumitval]
* added Cookie policy HTML Document [dumitval]
* logout page was broken by restricted objects raising Unauth. [simiamih]
* using %e to display day of mon without leading zero [simiamih]

3.1.9 (2012-10-23)
--------------------
* bulk email to users accepts json with custom mapping [simiamih]
* include Import users link in local users management [simiamih]

3.1.8 (2012-10-09)
--------------------
* refactored site logging admin view [simiamih]

3.1.7 (2012-10-09)
--------------------
* content types trigger view/download events [simiamih]
* added `notify_access_event` on NyContentType base class [simiamih]

3.1.6 (2012-10-09)
--------------------
* bugfix: adding role to local user in location with email
  notification [simiamih]

3.1.5 (2012-10-04)
--------------------
* revert ensure_tzinfo removal [simiamih]

3.1.4 (2012-10-04)
--------------------
* bugfix: #1004; undecoded value for role description [simiamih]

3.1.3 (2012-10-03)
--------------------
* #1000; user search in admin of notifications works
  with groupware [simiamih]

3.1.2 (2012-09-19)
--------------------
* bugfix in build_geo_filters [dumitval]

3.1.1 (2012-09-11)
--------------------
* bugfix in user search (notification admin page) [dumitval]

3.1.0 (2012-09-05)
--------------------
* #988 for Revoke searched user roles [simiamih]
* #988 also for pluguserfolder [simiamih]
* feature: #988 logging user management actions [simiamih]
* feature: #882 logging user actions in text files on disk [bogdatan]

3.0.9 (2012-08-28)
--------------------
* improved monitoring (extra info, zope sentry handler) [simiamih]

3.0.8 (2012-08-22)
--------------------
* added sentry error logging support [simiamih]
* bugfix: treating explicit folder parents zips [simiamih]
* more cleanup and code moved; photoarchive *needs* to be 1.3.10 [simiamih]

3.0.7 (2012-08-10)
--------------------
* Fix in loading skeleton (added files to skin) [dumitval]
* cleaning up obsolete code (NyVersions) [simiamih]

3.0.6 (2012-08-08)
--------------------
* fixed select-all checkbox in assign role to ldap users [simiamih]
* typo in email_requestrole [simiamih]

3.0.5 (2012-08-01)
--------------------
* updated pointers on obj move should be recataloged [simiamih]
* test fixes (fsbundles) [dumitval]

3.0.4 (2012-07-27)
--------------------
* fix in bundle name registration [dumitval]

3.0.3 (2012-07-24)
--------------------
* bugfix: ScriptChannel returns empty list if there is no Python code to be
  executed [bogdatan]

3.0.2 (2012-07-18)
--------------------
* Fixed naaya.core.utils.call_method() to work with
  Zope 2.12.23 too [bogdatan]

3.0.1 (2012-07-10)
--------------------
* added missing i18n:translate attribute on HTML tags [bogdatan]
* added some missing images from the old scheme [dumitval]
* renamed the skin and scheme back to the original ids [dumitval]

3.0.0 (2012-07-04)
--------------------
* Adapted folder_index, site_index and site_admin_template
  to work with the flowerpower standard_template [dumitval]
* Changed left_logo.gif [dumitval]
* Deleted old skin+scheme [dumitval]
* Adapted skin/standard_template to the new layout
  (the diff helps future updates of envirowindows, forum, etc) [dumitval]

2.13.20 (2012-07-04)
--------------------
* Allow id tag in portal editor anchor tags [dumitval]
* Code cosmetics on flowerpower standard_template [dumitval]
* update path for any pointers pointing to object on
  INyContentObjectMovedEvent [simiamih]

2.13.19 (2012-07-03)
--------------------
* Updates to element_header (flowerpower scheme) [dumitval]
* Added users_in_role rstk method [bogdatan]

2.13.18 (2012-06-28)
--------------------
* bugfix: temporary removed get_or_create_site_logger [bogdatan]
* Updates to slideshow.css [dumitval]
* bugfix: Folders excluded from latest uploads listing [bogdatan]

2.13.17 (2012-06-25)
--------------------
* get_http_proxy from buildout [dumitval]

2.13.16 (2012-06-20)
--------------------
* `Pillow` is now required dependency for Naaya [simiamih]
* *update* script: latestuploads_rdf uses latest_visible_uloads [simiamih]
* `Products.NaayaCore.managers.catalog_tool:latest_visible_uploads`
  [simiamih]
* tests for Products.NaayaCore.managers.catalog_tool [simiamih]
* Changed ReCaptcha warning message content and position [dumitval]
* bugfix: get_or_create_site_logger creates log path if does not
  exists [bogdatan]

2.13.15 (2012-06-13)
--------------------
* owners can now delete objects by checking them in folder view [simiamih]
* View for external applications to use authentication and standard
  template from a Naaya portal [moregale]
* External link for recaptcha [dumitval]
* Added two new utility functions: get_or_create_attribute,
  file_length [bogdatan]
* Changed get_or_create_site_logger format [bogdatan]

2.13.14 (2012-06-07)
--------------------
* cutoff level for walking subscriptions [simiamih]
* news_index: moved picture outside table [dumitval]
* removed in-file style from folder_listing [dumitval]
* added classes on some items [dumitval]
* updated some portlets to not show when empty [dumitval]
* map_admin_template.zpt: changed title [dumitval]
* Three lines of buttons on the portal editor [dumitval]
* Filesystem bundles have explicit parent configuration [moregale]

2.13.13 (2012-05-21)
--------------------
* Some new metadata on AnonymousSubscription [dumitval]

2.13.12 (2012-05-10)
--------------------
* bugfix: only (re)catalog INyCatalogAware on add/rm group role [simiamih]

2.13.11 (2012-05-04)
--------------------
* using ny_ldap_group_roles meta in catalog [simiamih]

2.13.10 (2012-04-27)
--------------------
* bugfix: AttributeError: generate_csv [nituacor]
* Bugfix in folder_administration_users [dumitval]

2.13.9 (2012-04-24)
--------------------
* Added buildout environment vars API keys to the administration
  API keys status page [bogdatan]
* Added title and description for API keys in administration API
  keys status page [bogdatan]

2.13.8 (2012-04-23)
--------------------
* Import content from Excel files [dumitval]

2.13.7 (2012-04-19)
--------------------
* Download HTML document from the object's index [dumitval]

2.13.6 (2012-04-17)
--------------------
* delete button for nyfolders [simiamih]
* view permission for Anonymous for portal_layout on creation [simiamih]
* starting to create mappings from errors to UI friendly texts [simiamih]

2.13.5 (2012-04-12)
--------------------
* added google analytics master profile [bogdatan]
* Fixed Analytics Tool test [bogdatan]

2.13.4 (2012-04-06)
--------------------
* bugfix in AuthenticationTool [simiamih]

2.13.3 (2012-04-06)
--------------------
* Added function to retrieve local roles for a specified user [bogdatan]
* fix FileIterator interface for zip download to work [simiamih]

2.13.2 (2012-04-05)
--------------------
* declared PortletsTool admin_layout as NaayaPageTemplateFile [dumitval]
* Added GA_ID and reCaptcha keys to Admin API Keys section [bogdatan]

2.13.1 (2012-04-04)
--------------------
* Comment box bug fix

2.13.0 (2012-04-03)
--------------------
* Added Akismet spam protection *update*
  (update_comments_add_spamstatus_property) [bogdatan]
* Created admin interface for managing comments *update*
  (update_portlet_administration_add_entries, update_css) [bogdatan]
* Created admin interface for API key status *update*
  (update_portlet_administration_add_entries, update_css) [bogdatan]
* Search for ga_id (analytics) also in buildout configuration [dumitval]
* site_manage_controlpanel compatibility fix for Zope 2.12 [dumitval]
* cleanup_message for feedback and request_role forms [dumitval]

2.12.80 (2012-03-27)
--------------------
* Added recaptcha on comment_add_html [dumitval]

2.12.79 (2012-03-27)
--------------------
* missing icon: indicator.gif
* new permission "Naaya - Create user" *update* [moregale]

2.12.78 (2012-03-26)
--------------------
* admin_bulk_mail_html fix for IE < 9 [dumitval]
* Skel - set content type for files in a scheme [moregale]

2.12.77 (2012-03-14)
--------------------
* Javascript fix for deselecting checkboxes [dumitval]
* Bugfix in admin_bulk_email [dumitval]

2.12.76 (2012-03-14)
--------------------
* added nofollow to zip download links [dumitval]
* code refactoring: Naaya - Zip export permission [simiamih]

2.12.75 (2012-03-12)
--------------------
* portlet administration - select portlet using "chosen" [moregale]

2.12.74 (2012-03-12)
--------------------
* Fully flexible portlet assignment from skel.xml [moregale]
* fix markup in templates, remove inline css [moregale]
* NyFolderBase allowed meta_types defaults to empty list [moregale]
* Allow adding files and folders in a portal_layout skin [moregale]

2.12.73 (2012-03-12)
--------------------
* strip javascript from textarea comments [dumitval]
* DiskFile can be converted to database File object [moregale]

2.12.72 (2012-03-09)
--------------------
* Update script to delete invalid pointers [dumitval]
* Added SyntaxError for incorrect date format [bogdatan]

2.12.71 (2012-03-07)
--------------------
* Atom feed - unicode bug fix in atom template [bogdatan]

2.12.70 (2012-03-05)
--------------------
* refactored media conversion + setting of aspect ratio property [dumitval]
* no subobjects for non-NyFolder objects (except NySite-s of course) [simiamih]
* fix in NySite.process_querystring - missing values in QUERYSTRING [simiamih]
* `uid` as default criteria in form for searching users in LDAP [simiamih]

2.12.69 (2012-03-01)
--------------------
* bugfix: folder_meta_types default when not found [simiamih]
* Fix glossary search for languages which are not in glossary
  languages list [bogdatan]
* Atom feed unicode bug fix [bogdatan]
* EmailTool.sendEmail should work without site [simiamih]

2.12.68 (2012-02-24)
--------------------
* fixed form submission in Assign User to Roles (ldap) on z2.12 [simiamih]
* added another ZIP mime type [bogdatan]
* naaya.core.zope2util.get_template_source wrapper [simiamih]

2.12.67 (2012-02-21)
--------------------
* Fix selector for jquery 1.7 in geomaptool.js [moregale]

2.12.66 (2012-02-21)
--------------------
* Added (back) example pins to admin_maptypes [dumitval]
* fixed folder listing form submission for all actions [bogdatan]
* Corrections to glossary.js - add a space after comma [dumitval]

2.12.65 (2012-02-17)
--------------------
* Email Delivery fix for zope 2.12 [simiamih]
* Upgrade to jQuery 1.7.1 [moregale]

2.12.64 (2012-02-16)
--------------------
* fixed sending immediate emails with repoze.sendmail 2.3 [simiamih]

2.12.63 (2012-02-16)
--------------------
* fixed localized file widget [nituacor]
* using repoze.sendmail instead of zope.sendmail for queuing [simiamih]

2.12.62 (2012-02-15)
--------------------
* typo in plugLDAPUserFolderGroupMembers - group email address [simiamih]

2.12.61 (2012-02-14)
--------------------
* Added permissions.zcml to be included in configure.zcml files [dumitval]
* NyPermissions.checkAllowedToZipImport [simiamih]

2.12.60 (2012-02-13)
--------------------
* Keep original movie resolution if re-encoding is needed [dumitval]
* Update script to add jquery-ui.css to standard template [dumitval]

2.12.59 (2012-02-10)
--------------------
* delete message dialog improvements [catardra]

2.12.58 (2012-02-10)
--------------------
* fixed pagination in tinymce [bogdatan]
* Added Terrain view to map layers [dumitval]

2.12.57 (2012-02-03)
--------------------
* Fix in ExportTool [dumitval]
* File widget and file download view [moregale]

2.12.56 (2012-02-01)
--------------------
* Added convert_to_user_string for use in csv_export [dumitval]
* Fixed convert_from_user_string for use in csv_import [dumitval]

2.12.55 (2012-01-25)
--------------------
* added plugLDAPUserFolder.get_local_roles_by_groups [simiamih]
* remove inline styles [moregale]
* ``naaya:simpleView`` directive [moregale]
* ``naaya:rstkMethod`` directive [moregale]

2.12.54 (2012-01-25)
--------------------
* fix update script to remove duplicate images [dumitval]

2.12.53 (2012-01-24)
--------------------
* fix for image id generation [dumitval]
* sha1_hash added to all images uploaded to the image storage [dumitval]
* update script to remove duplicates in the images storage [dumitval]

2.12.52 (2012-01-24)
--------------------
* interface for GeoMapTool [bogdatan]
* tiny mce default tab in advimage plugin [simiamih]
* Added last_modification property to NyContent types [dumitval]
* deprecated NyFolder.check_item_title calls removed [simiamih]
* allow for loading content from arbitrary skel folders [moregale]

2.12.51 (2012-01-18)
--------------------
* Update script to remove old properties for content types (now
  localized) [dumitval]

2.12.50 (2012-01-18)
--------------------
* update script to add photo related permissions to administrators [dumitval]
* added default permission for Photo Folder and Gallery to admins [dumitval]

2.12.49 (2012-01-17)
--------------------
* GeoMap: added filtering option for topics [dumitval]
* added LinkedIn logo [dumitval]
* bugfix: dotted property clashed with reserved word - IE8 [simiamih]
* bugfix: collapsing folder in mainsections does not hide link [simiamih]

2.12.48 (2012-01-16)
--------------------
* removed get_modification_date from NyContentTypeViewAdapter [dumitval]
* fixed a string in SelectMultipleWidget.py to allow translation [dumitval]
* added i18n:translate to help_text of widgets [dumitval]

2.12.47 (2012-01-13)
--------------------
* support translation_id in widget properties,
  and make use of it in select widgets [dumitval]
* Added i18n id for translation of 'Type' [dumitval]

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
