Changelog
=========

2.10.12 (unreleased)
--------------------
 * Zip export uses temporary file instead of building archive in memory.

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
