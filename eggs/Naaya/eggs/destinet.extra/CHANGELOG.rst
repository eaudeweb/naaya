1.1.5 (unreleased)
====================

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

