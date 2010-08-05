import os.path

from zope.component import getAdapter
from App.ImageFile import ImageFile

from contentratings.interfaces import IUserRating

def imagePath(rating):
    return os.path.join(os.path.dirname(__file__), 'www',
            'Picture%d.png' % rating)

class RatingOutOfBoundsError(Exception):
    def __init__(self, rating):
        self.rating = rating
    def __str__(self):
        return 'rating is %d' % self.rating

class ObservatoryRatingView(object):
    """A view for getting the rating information"""

    ratingImages = [ImageFile(imagePath(rating)) for rating in range(5)]

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

    def __call__(self, REQUEST, RESPONSE):
        rating = int(round(self.averageRating))
        if not (0 <= rating < 5):
            raise RatingOutOfBoundsError(rating)

        return self.ratingImages[rating].index_html(REQUEST, RESPONSE)

