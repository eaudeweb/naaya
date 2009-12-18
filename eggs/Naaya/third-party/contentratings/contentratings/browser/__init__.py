# some BBB imports
from zope.deferredimport import deprecatedFrom

deprecatedFrom('The old style rating views are no longer intended to be used.'
               'Use the aggregator and rating views instead.  These views will '
               'go away in version 1.1',
               'contentratings.browser.bbb', 'EditorialRatingView',
               'EditorialRatingSetView', 'UserRatingView', 'UserRatingSetView',
               'MacroProvider')
