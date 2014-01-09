1.2.15 (2014-01-09)
====================
* Bug fix: make the landscape and topic widgets required if a value is 
  set in organization/marketplace/supporting solutions widgets
  [tiberich #17641]

1.2.14 (2014-01-08)
====================
* Bug fix: don't fail when adding a contact with root acl user
  [tiberich #17641]

1.2.13 (2014-01-08)
====================
* Bug fix: make the postal address / geo_location fields take
  value from each other if one of them is missing value
  [tiberich #17641]
* correct releasedate for contacts created for users [dumitval]
* Bug fix: redo the update script that creates contacts for old users
  [tiberich Destinet #17641]
* Bug fix: also show the group widget on the show_on_atlas page
  [tiberich Destinet #17641]

1.2.12 (2013-12-18)
====================
* Bug fix: added dependency on Naaya 3.3.24, because of needed API
  [tiberich Destinet #17642]

1.2.11 (2013-12-18)
====================
* Feature: added migration code for destinet users that have no Naaya Contact attached
* Feature: Added migration code to set the "Destinet user" keyword to all Naaya Contact entries
  attached to users; 
* Feature: Added migration code to change schema for NaayaContact
* Feature: Split category field in 3 other properties 
  (category-organization, category-marketplace, category-supporting-solution). 
* Feature: Add these 3 fields to the contact_index template (in DESTINET bundle)
* Feature: Deprecate and automatically fill in the geo_type property with a value from one of the 3
  new categories, using subscription handlers on add/modify events
  [tiberich #17643 Destinet, 17644 Destinet]

1.2.10 (2012-12-14)
====================
* removed redundant geocoding (now done by the widget) [dumitval]

1.2.9 (2012-12-11)
====================
* recatalog object in handle_groups [dumitval]

1.2.8 (2012-12-11)
====================
* bugfix (call handle_groups after manageProperties) [dumitval]

1.2.7 (2012-12-10)
====================
* do_geocoding on newly created contacts [dumitval]

1.2.6 (2012-12-10)
====================
* add keyword to new users if group members [dumitval]

1.2.5 (2012-12-10)
====================
* bugfix ref special role [dumitval]

1.2.4 (2012-12-10)
====================
* add a special role ("EEN Members") to some of the new users [dumitval]

1.2.3 (2012-08-22)
====================
* different way of finding linked contact object (catalog based) [simiamih]

1.2.2 (2012-08-03)
====================
* added user groups in registration; side-effect: pointer in designated
  `new applicants` folder [simiamih]

1.2.1 (2012-08-02)
====================
* new user instantly receives Contributor role [simiamih]
* comments have been rebranded as About me and saved on contact [simiamih]
* pointers also for many meta type objs added in who-who [simiamih]

1.2.0 (2012-07-20)
====================
* refactored unit testing code [simiamih]
* feature: destinet custom registration; needs interface assigned to portal
  from ZMI and bundles updated [simiamih]

1.1.12 (2012-07-04)
====================
* approve/unapprove object action is performed on synced pointers [simiamih]

1.1.11 (2012-05-10)
====================
* enhancements for admin_assign_role_html [dumitval]
* Bugfix in adding Naaya Publications
* publishing unit test: test logging for missing country [simiamih]

1.1.10 (2012-04-18)
====================
* country folders must match title exactly for pointers [simiamih]
* subscribers updated to create pointers for NyBFile too [simiamih]

1.1.9 (2012-03-20)
====================
* speed up login_html using ajax calls [dumitval]

1.1.8 (2012-03-16)
====================
* Bugfix in editor role assignment [dumitval]
* Adapt keywords functionality to work with standard folder listing [dumitval]

1.1.7 (2012-03-05)
====================
* Filter by contributor instead of author (publishing) [dumitval]

1.1.6 (2012-02-17)
====================
* unicode encode bug fix [bogdatan]

1.1.5 (2012-02-17)
====================
* Recatalog objects after savingt their keywords [bogdatan]

1.1.4 (2012-02-14)
====================
* fixed some security declarations in DestinetPublisher [simiamih]
* Corrected to set keywords as local property [bogdatan]
* Imported permissions.zcml allow zope2.NaayaPublishContent permission [dumitval]
* Corrected permission for allocateKeywords and allocate_keywords_html [dumitval]

1.1.3 (2012-01-31)
====================
* fix for objects with no __ac_local_roles__ [dumitval]
* all zcml configures linked in destinet.extra/configure.zcml [simiamih]

1.1.2 (2012-01-30)
====================
* Possibility to add local role "Editor" to contributors [dumitval]

1.1.1 (2012-01-24)
====================
* pointers referred by target_groups are now placed in subdirs of resources,
  and not who-who [simiamih]
* added messages when there's nothing to submit or the referer
  is empty [bogdatan]

1.1 (2012-01-24)
====================
* added destinet.keywords - Keywords allocation system [bogdatan]
* publisher: fix in copying data to pointer [simiamih]

1.0 (2012-01-19)
====================
* initial release, destinet.publishing customization [simiamih]

