1.1.12 (unreleased)
====================

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

