Patch to add NotificationList object to Naaya sites
===================================================

This product monkey-patches the Naaya product, hooking on to the administrator
notification method to allow notification of changes to arbitrary users.

To use this product, one must add the "Naaya Folder Notification List" content
type to the "Subobjects" list of types of a folder, and create an instance
named "notification_list" inside the folder. This ID is important,
notifications will not be sent if the object has another ID.
