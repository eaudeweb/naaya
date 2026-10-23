2.0.4 (unreleased)
------------------

2.0.3 (2026-10-23)
------------------
* Give the methods with a blank docstring a text: Python 3.13 strips it to ''
  and Zope does not publish methods without a docstring [dumitval]
* Close the RDF feed response after reading it [dumitval]
* Use standard_template_macro instead of the deprecated
  standard_html_header/footer in the templates [dumitval]

2.0.2 (2026-10-23)
------------------
* Remove the Python deprecation warnings [dumitval]
* Fix and extend the tests [dumitval]

2.0.1 (2026-10-16)
------------------
* Fix the test modules syntax for Python 3 [dumitval]
* Read the RDFSummary test feed from a local file instead of the network
  [dumitval]

2.0.0 (2026-10-12)
------------------
* Port RDFCalendar and RDFSummary to Python 3 and Zope 5 [dumitval]
* Use a PEP 420 namespace package for Products [dumitval]

1.0.3 (2018-03-15)
----------------
* vulnerability fix [dumitval]

1.0.2 (2016-11-22)
----------------
* add os environ to zope environment [dumitval]

1.0.1 (2012-05-18)
----------------
* Fix index crash when no year is provided + update script [dumitval]

1.0 (2012-03-08)
----------------
* better way to access buildout environment vars [simiamih]
* Re-packaging of Zope2 products RDFCalendar 1.1 and RDFSummary 3.0.1 into
  single Python package [moregale]
* Compatibility with Zope 2.12 and feedparser 5.0.1 [moregale #4511]
