2.0.1 (unreleased)
------------------
* Use the standard library json instead of simplejson [dumitval]

2.0.0 (2026-10-12)
------------------
* Port to Python 3 and Zope 5 [dumitval]
* Fix the photo display pages and generating or purging displays [dumitval]
* Fix single image upload, zip upload adding no photos and zip downloads with
  empty files [dumitval]
* Use PEP 420 namespace packages [dumitval]

1.5.2 (2015-10-23)
-------------------
* small CSS improvement

1.5.1 (2014-10-10)
-------------------
* moved update script to another package [dumitval]

1.5.0 (2014-10-09)
-------------------
* Feature: now using Naaya Blob files instead of Naaya ExtFiles to store
  images
  [tiberich #3929]
* Bug fix: don't fail on view of non-migrated Photos
  [tiberich #3929]

1.4.0 (2013-02-25)
-------------------
* replaced the old slideshow functionality by a lightbox library
* replaced misc_ by browser:resourceDirectory (zcml)
* removed localizer reference (leftover)
* structural html improvements in photo_index.zpt

1.3.10 (2012-08-22)
-------------------
* importing register_naaya_permissions as in Naaya 3.0.7 [simiamih]

1.3.9 (2012-03-14)
------------------
* use permission for exporting zip of photo folder [simiamih]

1.3.8 (2011-11-14)
------------------
* permission information update [andredor]

1.3.7 (2011-10-31)
------------------
* fix indexes translations [andredor]

1.3.6 (2011-10-18)
------------------
* save contributor for NyPhoto and NyPhotoFolder [andredor]
