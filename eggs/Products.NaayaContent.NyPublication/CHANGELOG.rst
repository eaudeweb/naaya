2.0.4 (unreleased)
------------------

2.0.3 (2026-10-23)
------------------
* Give the methods with a blank docstring a text: Python 3.13 strips it to ''
  and Zope does not publish methods without a docstring [dumitval]
* Use utSlugify instead of the deprecated utCleanupId [dumitval]

2.0.2 (2026-10-23)
------------------
* Fix and extend the tests [dumitval]

2.0.1 (2026-10-20)
------------------
* Remove the Checkout link from the publication index; publications have
  no versioning and startVersion failed with TypeError [dumitval]

2.0.0 (2026-10-12)
------------------
* Port to Python 3 and Zope 5 [dumitval]
* Fix the XML import storing text fields as bytes [dumitval]
* Use PEP 420 namespace packages [dumitval]

1.1.9 (2015-03-12)
------------------
* reCaptcha 2.0 compatibility [dumitval]

1.1.8 (2014-12-08)
------------------
* python 2.6 compatibility (raising errors) [dumitval]

1.1.7 (2014-11-24)
------------------
* check_item_title is now item_has_title [simiamih]
* Bug fix: compatibility with NyFSFile with blobs
  [tiberich #3929]

1.1.6 (2012-01-13)
------------------
* Added i18n id for translation of 'Type' [dumitval]

1.1.5 (2011-12-16)
------------------
* event notifications: NyContentObjectAddEvent and Edit [simiamih]

1.1.4 (2011-12-07)
------------------
* addNyPublication returns object when referer not a known one [simiamih]

1.1.3 (2011-11-17)
------------------
* portal_map methods are no longer called if the content type is not
 geo_enabled [dumitval]

1.1.2 (2011-11-14)
------------------
* permission information update [andredor]

1.1.1 (2011-10-24)
------------------
* add forms use reCAPTCHA [andredor]

1.1 (2010-11-01)
----------------
* Fix save changes date problem on index page (#413)

1.0 (2010-08-05)
----------------
* Initial release

