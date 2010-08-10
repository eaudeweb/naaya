import os.path

from zope.component import getAdapter
from zope.traversing.namespace import getResource
import zLOG

from contentratings.interfaces import IUserRating
from contentratings.browser.bbb import UserRatingSetView

from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

class RatingOutOfBoundsError(Exception):
    def __init__(self, rating):
        self.rating = rating
    def __str__(self):
        return 'rating is %d' % self.rating

class ObservatoryRatingView(object):
    """A view for getting the rating information"""

    FILE_NAMES = ['Very bad', 'Bad', 'Average', 'Good', 'Very good']

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')

        assert int(self.adapted.scale) == 5

    @property
    def rating(self):
        return int(round(self.adapted.averageRating))

    def __call__(self, REQUEST):
        if not (0 <= self.rating < 5):
            raise RatingOutOfBoundsError(self.rating)

        resource = self.context.unrestrictedTraverse(
                '++resource++naaya.observatory.contentratings/images/%s.png'
                    % self.FILE_NAMES[self.rating])
        return resource.GET()

class ObservatoryRatingCommentsView(object):
    """A view for rating and comments"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')
        self.message = context.getPortalTranslations()

        assert int(self.adapted.scale) == 5

    @property
    def rating(self):
        return int(round(self.adapted.averageRating))

    @property
    def comments_list(self):
        return self.context.get_comments_list()

class ObservatoryRatingSetView(UserRatingSetView):
    """A view for setting the rating information"""

    #Overwriting this to have different keys for observatory ratings
    KEYBASE = 'observatory-anon-rated-'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')
        self.message = context.getPortalTranslations()

        assert int(self.adapted.scale) == 5

    @property
    def address(self):
        address = self.context.geo_address()
        if address:
            return address

        if not self.context.geo_location:
            return ''
        if self.context.geo_location.missing_lat_lon:
            return ''

        lat = self.context.geo_latitude()
        lon = self.context.geo_longitude()
        try:
            return reverse_geocode(lat, lon)
        except GeocoderServiceError, e:
            zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
            return ''

    def rate_and_comment(self, type, rating, comment='', orig_url=None):
        """
        Rate and comment an object
        attempts to redirect back to the original url
        """
        if comment:
            context = self.context.aq_self
            context.comment_add(body=comment)

        self.rate(rating, orig_url)



