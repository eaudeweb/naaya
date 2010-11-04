Changelog
=========

2.10.10 (unreleased)
--------------------
 * ProfilesTool refactored to subclass from BTreeFolder2. Update script:
   `Change ProfilesTool to use BTree`.
 * ProfilesTool moved from NaayaCore to Products.NaayaProfilesTool because it
   is rarely used and shouldn't be in the Core
 * Major interface update for Products.NaayaCore.AuthenticationTool.
   Added ajax interface in user management (administration), fixed a lot of
   bugs.
 * Fix: NotificationTool subscriptions - strip user_id spaces. The update
   script `Remove spaces from ...` will remove existing spaces.
 * Feature: user password reset with email verification
 * Fix: templates customized in ``portal_forms`` now accept ``**kwargs``
 * Refactoring for code that walks a `RefTree`
 * Improvements to DiskFile object; new DiskTemplate object; can be added
   from ``skel.xml``.
 * User management LDAP improvements:
   - Tabbed page: `manage roles`, `assign users roles`, `assign groups roles`
   - Ajax search and sorting.
   - Getting user information performance improvement.
 * Meta tags for all content types (index pages). Includes: `description`,
   `keywords`, `contributor`, `dc.language` and `title`
 * Fix: Permissions editor getting target object
 * Permissions editor shows acquired permissions for the object

2.10.9 (2010-10-06)
-------------------
 * First numbered version
