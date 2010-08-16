import os.path

from zope.traversing.namespace import getResource
import zLOG
from Products.Five.browser import BrowserView

from contentratings.interfaces import IUserRating
from contentratings.browser.bbb import UserRatingSetView

from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

RESOURCES_PATH = '++resource++naaya.observatory.contentratings'
IMAGES_PATH = RESOURCES_PATH + '/images'

RATING_IMAGE_NAMES = ['Very Bad', 'Bad', 'Average', 'Good', 'Very good']
RATING_IMAGE_PATHS = ['%s/%s.png' % (IMAGES_PATH, f)
                        for f in RATING_IMAGE_NAMES]

TYPE_IMAGE_NAMES = ['Vegetation', 'Water', 'Soil', 'Citizens']
TYPE_IMAGE_PATHS = ['%s/%s.png' % (IMAGES_PATH, f)
                    for f in TYPE_IMAGE_NAMES]

class RatingOutOfBoundsError(Exception):
    def __init__(self, rating):
        self.rating = rating
    def __str__(self):
        return 'rating is %d' % self.rating

class ObservatoryRatingView(BrowserView):
    """A view for getting the rating information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def resources_path(self):
        return RESOURCES_PATH

    @property
    def rating_range(self):
        return range(5)

    @property
    def rating(self):
        return int(round(self.context.averageRating))

    def rating_image_paths(self, rating):
        return RATING_IMAGE_PATHS[rating]
    @property
    def rating_image_path(self):
        return self.rating_image_paths(self.rating)

    @property
    def type(self):
        return 1

    def type_image_paths(self, type):
        return TYPE_IMAGE_PATHS[type]
    @property
    def type_image_path(self):
        return self.type_image_paths(self.type)

    @property
    def type_message(self):
        translations_tool = self.context.getPortalTranslations()
        return translations_tool(self.TYPE_MESSAGES[self.type])

    def rating_messages(self, rating):
        translations_tool = self.context.getPortalTranslations()
        return translations_tool(self.RATING_MESSAGES[rating])
    @property
    def rating_message(self):
        return self.rating_messages(self.rating)

    def rating_titles(self, rating):
        translations_tool = self.context.getPortalTranslations()
        return translations_tool(self.RATING_TITLES[rating])
    @property
    def rating_title(self):
        return self.rating_titles(self.rating)

    def rating_alts(self, rating):
        translations_tool = self.context.getPortalTranslations()
        return translations_tool(self.RATING_ALTS[rating])
    @property
    def rating_alt(self):
        return self.rating_alts(self.rating)

    def rating_image(self, REQUEST):
        if not (0 <= self.rating < 5):
            raise RatingOutOfBoundsError(self.rating)

        resource = self.context.unrestrictedTraverse(self.rating_image_path)
        return resource.GET()

class ObservatoryRatingCommentsView(ObservatoryRatingView):
    """A view for rating and comments"""

    RATING_MESSAGES = ['Very bad', 'Bad', 'Average', 'Good', 'Very good']
    RATING_TITLES = ['Vote %s' % l for l in RATING_MESSAGES]
    RATING_ALTS = list(RATING_MESSAGES)

    TYPE_MESSAGES = ['Vegetation', 'Water', 'Soil', 'Citizen reported']

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def address(self):
        lat = self.context.latitude
        lon = self.context.longitude
        try:
            return reverse_geocode(lat, lon)
        except GeocoderServiceError, e:
            zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
            return ''

    @property
    def comments_list(self):
        return []
        # TODO
        #return self.context.get_comments_list()

class ObservatoryRatingSetView(UserRatingSetView,
                               ObservatoryRatingCommentsView):
    """A view for setting the rating information"""

    #Overwriting this to have different keys for observatory ratings
    KEYBASE = 'observatory-anon-rated-'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.message = context.getPortalTranslations()

    def rate_and_comment(self, type, rating, comment='', orig_url=None):
        """
        Rate and comment an object
        attempts to redirect back to the original url
        """
        if comment:
            context = self.context.aq_self
            context.comment_add(body=comment)

        self.rate(rating, orig_url)



