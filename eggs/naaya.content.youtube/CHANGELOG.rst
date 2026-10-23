2.0.2 (unreleased)
------------------
* Give the methods with a blank docstring a text: Python 3.13 strips it to ''
  and Zope does not publish methods without a docstring [dumitval]
* Close the HTTP error of a rejected video check [dumitval]

2.0.1 (2026-10-23)
------------------
* Remove the Python deprecation warnings from the tests [dumitval]
* Fix the video check failing when youtube.com cannot be reached [dumitval]
* Fix and extend the tests [dumitval]

2.0.0 (2026-10-12)
------------------
* Port to Python 3 and Zope 5 [dumitval]
* Use PEP 420 namespace packages [dumitval]

1.0.5 (2021-04-09)
------------------
* remove plain http from everywhere [dumitval]

1.0.4 (2015-10-19)
------------------
* updated to youtube API v.3 (checking for existing video ID) [dumitval]

1.0.3 (2015-03-11)
------------------
* reCaptacha compatibility [dumitval]

1.0.2 (2014-07-03)
------------------
* avoid related videos at the end of playback [dumitval]

1.0.1 (2013-04-25)
------------------
* Youtube video URL are now accepted, too [dumitval]
* extended test_add_error to use an invalid youtube video id [dumitval]

1.0.0 (2013-03-27)
------------------
* first version [dumitval]
