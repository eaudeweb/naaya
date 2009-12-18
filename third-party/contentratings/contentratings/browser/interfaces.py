from zope.interface import Interface
from zope.deferredimport import deprecatedFrom

class IRatingView(Interface):
    """A Marker indicating a rating view"""

class IAnonymousSession(Interface):

    def get_anon_key(request):
        """Generates a unique key for the current browser to ensure
        anonymous ratings can be restricted"""

deprecatedFrom('The old style rating views are no longer intended to be used.'
               'Use the aggregator and rating views instead.  This interface '
               'will go away in version 1.1',
               'contentratings.browser.bbb.interfaces', 'IEditorialRatingView')
