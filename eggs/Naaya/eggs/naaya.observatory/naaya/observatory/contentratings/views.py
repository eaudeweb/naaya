import os.path

from zope.component import getAdapter
from zope.traversing.namespace import getResource
import zLOG

from contentratings.interfaces import IUserRating

from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

class RatingOutOfBoundsError(Exception):
    def __init__(self, rating):
        self.rating = rating
    def __str__(self):
        return 'rating is %d' % self.rating

class ObservatoryRatingView(object):
    """A view for getting the rating information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')

        assert int(self.adapted.scale) == 5

    @property
    def averageRating(self):
        return self.adapted.averageRating

    @property
    def numberOfRatings(self):
        return self.adapted.numberOfRatings

    @property
    def scale(self):
        return self.adapted.scale

    @property
    def rating(self):
        return int(round(self.averageRating))

    def __call__(self, REQUEST):
        if not (0 <= self.rating < 5):
            raise RatingOutOfBoundsError(self.rating)

        resource = getResource(self.context.getSite(),
                'naaya.observatory_rating_%d.icon' % self.rating, REQUEST)
        return resource.GET()

class ObservatoryRatingSetView(object):
    """A view for setting the rating information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')

        assert int(self.adapted.scale) == 5

    @property
    def averageRating(self):
        return self.adapted.averageRating

    @property
    def numberOfRatings(self):
        return self.adapted.numberOfRatings

    @property
    def scale(self):
        return self.adapted.scale

    @property
    def rating(self):
        return int(round(self.averageRating))

    def userRating(self, REQUEST):
        user = REQUEST.AUTHENTICATED_USER.getUserName()
        return self.adapted.userRating(user)

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
            zLOG.LOG('naaya.observatory', zLOG.INFO, str(e))
            return ''

    def rate(self, rating, REQUEST, orig_url=None):
        """ Rate an object, attempts to redirect back to the original url """
        user = REQUEST.AUTHENTICATED_USER.getUserName()
        self.adapted.rate(rating, user)
        if orig_url is not None:
            return REQUEST.RESPONSE.redirect(orig_url)

