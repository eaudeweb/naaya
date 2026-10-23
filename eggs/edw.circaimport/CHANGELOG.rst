2.0.2 (unreleased)
------------------
* Remove the Python deprecation warnings [dumitval]
* Fix and extend the tests [dumitval]
* Remove the circaimport console script and DemoActor, broken since 2012
  [dumitval]

2.0.1 (2026-10-16)
------------------
* Read the redirect config and LDIF files as UTF-8 [dumitval]
* Fix the CIRCA files and folders import failing with bytes/str errors when
  reading the zip index and members [dumitval]
* Fix the CIRCA roles import skipping all LDIF entries because python-ldap
  returns the values as bytes [dumitval]
* Fix the CIRCA notifications and ACLs imports failing to parse the exported
  files opened in binary mode [dumitval]
* Fix the CIRCA ACLs import failing when the file has no profile entries
  [dumitval]
* Fix import_all_from_circa not passing the notification type to the
  notifications import [dumitval]
* Fix the import report log formatter failing on messages that contain "%"
  [dumitval]
* Fix zimport_data failing to format the error of an unreadable zexp file
  [dumitval]
* Fix the circaimport console script failing on the lang argument of
  DemoActor.document_entry [dumitval]

2.0.0 (2026-10-12)
------------------
* Port to Python 3 and Zope 5 [dumitval]
* Require Naaya >= 6.0.1 and naaya.groupware >= 2.0.0 [dumitval]
* Use PEP 420 namespace packages [dumitval]
* Fix the zexp copy failing to read the export path from the Zope 5
  export message [dumitval]

1.3.14 (2023-09-20)
------------------
* add count.txt to zip_export from console
  [valipod refs #257967]

1.3.13 (2023-02-07)
------------------
* add zip_export to console scripts
  [valipod]

1.3.12 (2020-12-14)
------------------
* try import with default filename (site id) if none given (acls,
  notifications) [dumitval]

1.3.11 (2020-12-11)
------------------
* try import with default filename (site id) if none given (files) [dumitval]

1.3.10 (2020-12-11)
------------------
* add files in another language, if detected [dumitval]
* try import with default filename (site id) if none given (ldif) [dumitval]

1.3.9 (2020-04-13)
------------------
* small template change to work with the new Eionet layout [dumitval]

1.3.8 (2019-12-04)
------------------
* bugfix when importing whole ig [dumitval]

1.3.7 (2019-11-18)
------------------
* compatibility fix for Pluggable Auth Service [dumitval]

1.3.6 (2019-10-18)
------------------
* improve import success message for complete ig import [dumitval]

1.3.5 (2019-10-17)
------------------
* improve import/export procedure [dumitval]

1.3.4 (2016-11-22)
------------------
* add os environ to zope environment [dumitval]

1.3.3 (2014-10-09)
------------------
* further keys handling [dumitval]

1.3.2 (2014-10-08)
------------------
* handle dictionary keys in different casing [dumitval]

1.3.1 (2014-09-29)
------------------
* bugfix when notifications are disabled (import_all_from_circa) [dumitval]

1.3.0 (2012-08-28)
------------------
* new feature (sub product): zexp export/import between instances [simiamih]

1.2 (2012-06-20)
------------------
* circa circle name configurable from environ var CIRCA_CIRCLE_NAME [simiamih]
* make it possible to import files in batches (merge imports) [simiamih]
* also aq_foo or bar__ ids are not allowed in zope [simiamih]
* better .url files parsing and no url renaming [simiamih]

1.1 (2012-02-22)
------------------
* added circa_redirect feature [simiamih]

1.0.1 (2012-02-02)
------------------
* correct usage of mimetypes.guess_type [simiamih]

1.0.0 (2012-01-05)
------------------
* First numbered version [dumitval]
