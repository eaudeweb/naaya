= Migration of CIRCA interest groups to Forum =

Migrating folders and users(membership information):
 * You manually export folders from CIRCA using the "save" button. The "download" button, next to it, does not save enough information. This should export a zip file.
 * You manually export user roles from CIRCA using the "IG save" button (CIRCA's backup feature). The "save" button, does not save members information. This should export a tgz file.
 * Save files from CIRCA, copy them to !root@kitten.eea.europa.eu:/var/local/forum/data_volume/temp/circa_import/
 * Check that the file from CIRCA is complete.
 * Check that there are read permissions after the copy
 * Navigate to the new interest group, in the Library folder, request the web page `import_files_from_circa_html` and enter the filename.
 * Navigate to the new interest group, request the web page `import_roles_from_circa` and enter the filename and the LDAP source (find it from 'User management' in the admin area or from acl_users in ZMI for managers, usually 'LDAP' or 'Eionet').
 * Files bigger than 1 GB can cause the webbrowser to timeout. The import is still going on to the end.
 * On CIRCA you use the administration interface to archive the IG.
 * Remember to check that the archive is complete before you delete the IG. The archives are located at /opt/circa21/www/data/eionet-circle/Backup

Migrating notification subscriptions:
 * Log in to dodo as circa21 (will ensure you use the correct Perl libraries)
 * Copy (for safety) the db files to a workarea (e.g. the 'scp' IG are located at /opt/circa21/www/data/eionet-circle/scp/library/ we need the usernotification.db)
 * You can then run /usr/local/bin/circadbprint on a file. It will convert the database to a printable format. Save the output to a file (e.g. user_notification.txt)
 * Copy the file to !root@kitten.eea.europa.eu:/var/local/forum/data_volume/temp/circa_import/
 * Navigate to the new interest group, request the web page `import_notifications_from_circa` and enter the filename.

Migrating ACLs:
 * Log in to dodo as circa21 (will ensure you use the correct Perl libraries)
 * Copy (for safety) the db file to a workarea (e.g. the 'scp' IG are located at /opt/circa21/www/data/eionet-circle/nfp-eionet/library/ we need the itemacls.db)
 * You can then run /usr/local/bin/circadbprint on a file. It will convert the database to a printable format. Save the output to a file (e.g. itemacls.txt)
 * Copy the file to !root@kitten.eea.europa.eu:/var/local/forum/data_volume/temp/circa_import/
 * Navigate to the new interest group, request the web page `import_acls_from_circa` and enter the filename.

Migrating everything at once:
 * Get the exported files to !root@kitten.eea.europa.eu:/var/local/forum/data_volume/temp/circa_import/ (as in the previous steps)
 * Navigate to the new interest group, request the web page `import_all_from_circa` and enter the filenames and additional data. Every migration is optional (e.g. if you didn't export the notifications, just leave the 'Notifications exported file:' field empty)
 * Here you also have the option to just get the report (NO import is actually done if you click the report button)
