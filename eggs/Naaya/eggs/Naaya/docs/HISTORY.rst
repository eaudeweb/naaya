Changelog
=========

2.10.11 (unreleased)
--------------------

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
