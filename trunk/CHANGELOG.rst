1.4.7 (2014-10-29)
--------------------
* Bug fix: issue warnings when extfile is broken
  [tiberich #3929

1.4.6 (2014-10-29)
--------------------
* PEP8 code formatting in some files [dumitval]
* strip leading underscores from new filenames [dumitval]
* Bug fix: added migration for naaya.content.talkback comment attachments
  [tiberich #3929]
* Bug fix: added migration for naaya survey attachment files
  [tiberich #3929]

1.4.5 (2014-10-24)
--------------------
* strip leading underscores from the filename in download url [dumitval]

1.4.4 (2014-10-10)
--------------------
* added an error handling on update script NyFile2NyBlob [dumitval]

1.4.3 (2014-10-10)
--------------------
* improve update scripts for migration from NyFile and NyExtFile to Blob
  [tiberich

1.4.2 (2014-10-10)
--------------------
* `update` execute the 'PhotoArchive and MediaFiles: Migrate ExtFiles to Blobs'
  migration to properly migrate the photoarchive  and media files to blob
  storage [tiberich #3929]

1.4.1 (2014-10-10)
--------------------
* improve extfile to bfile update scripts to delete original files [dumitval]

1.4.0 (2014-10-09)
--------------------
* Merge with the no-extfile branch
  [tiberich #3929]

1.3.14 (2014-04-04)
--------------------
* bugfix related to comments to removed versions [dumitval]
* bugfix related to incorrect timezone conversion [dumitval]

1.3.13 (2014-03-05)
--------------------
* Allow pairing of comments with document versions [dumitval]

1.3.12 (2013-07-10)
--------------------
* link to the contributor profile from the index page [dumitval]

1.3.11 (2013-05-17)
--------------------
* #4547 comment#9; bfile_index tpl small changes in labels [simiamih]

1.3.10 (2013-02-22)
--------------------
* newest versions first [simiamih]

1.3.9 (2012-12-19)
------------------
* #10213 - eliminate redundant notifications sent by zip upload [mihaitab]
* opening file index page is not a view event [simiamih]

1.3.8 (2012-10-09)
------------------
* view/download events are triggered [simiamih]

1.3.7 (2012-10-04)
------------------
* revert ensure_tzinfo removal [simiamih]

1.3.6 (2012-10-04)
------------------
* version timestamps are saved with tzinfo [simiamih]
* Added 'Uploaded by' column in versions table [bogdatan]

1.3.5 (2012-07-18)
------------------
* Added contributor to versions [bogdatan]
* check_item_title is now item_has_title [simiamih]
* fixed adapter to work with localizedbfile [simiamih]

1.3.4 (2012-01-13)
------------------
* Added i18n id for translation of 'Type' [dumitval]

1.3.3 (2011-11-17)
------------------
* portal_map methods are no longer called if the content type is not
  geo_enabled [dumitval]

1.3.2 (2011-11-14)
------------------
* permission information update [andredor]
