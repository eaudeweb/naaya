Changelog
=========

2.10.10 (unreleased)
--------------------
 * ProfilesTool refactored to subclass from BTreeFolder2. Update script:
   `Change ProfilesTool to use BTree`.
 * Fix: NotificationTool subscriptions - strip user_id spaces. The update
   script `Remove spaces from ...` will remove existing spaces.
 * Feature: user password reset with email verification
 * Fix: templates customized in ``portal_forms`` now accept ``**kwargs``
 * Refactoring for code that walks a `RefTree`
 * Improvements to DiskFile object; new DiskTemplate object; can be added
   from ``skel.xml``.

2.10.9 (2010-10-06)
-------------------
 * First numbered version
