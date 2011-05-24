# Everything here is intended for BBB only, do not use these views

from zope.interface import implements, Interface
from zope.location.interfaces import ISublocations
from zope.i18nmessageid import MessageFactory
try:
    from Products.statusmessages.interfaces import IStatusMessage
except ImportError:
    # Dummy
    class IStatusMessage(Interface):
        pass

from contentratings.interfaces import IEditorialRating
from contentratings.interfaces import IUserRating
from contentratings.interfaces import _

#from contentratings.browser.interfaces import IEditorialRatingView
# TODO warning disabled, it's not likely to be fixed anytime soon
from interfaces import IEditorialRatingView


try:
    from AccessControl import getSecurityManager
    ZOPE3= False
except ImportError:
    ZOPE3 = True

class EditorialRatingView(object):
    """A view for getting the rating information"""

    implements(IEditorialRatingView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = IEditorialRating(context)

    def _getRating(self):
        return self.adapted.rating
    rating = property(_getRating)

    def _getScale(self):
        return self.adapted.scale
    scale = property(_getScale)


class EditorialRatingSetView(EditorialRatingView):
    """A view for setting the rating information"""

    def rate(self, rating, orig_url=None):
        """Rate an object"""
        self.adapted.rating = rating
        self.post_rate(orig_url)

    def post_rate(self, orig_url=None):
        if orig_url is not None:
            message = '%s' % _('You have changed your rating').decode('utf-8')
            q_spacer= '?' in orig_url and '&' or '?'
            messages = IStatusMessage(self.request, alternate=None)
            if messages is not None:
                messages.addStatusMessage(message, 'info')
            res = self.request.RESPONSE
            return res.redirect(orig_url+q_spacer)


class UserRatingView(object):
    """A view for getting the rating information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = IUserRating(context)

    def _average(self):
        return self.adapted.averageRating
    averageRating = property(_average)

    def _number(self):
        return self.adapted.numberOfRatings
    numberOfRatings = property(_number)

    def _getScale(self):
        return self.adapted.scale
    scale = property(_getScale)


class UserRatingSetView(object):
    """A view for setting the rating information"""

    KEYBASE = 'anon-rated-'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = IUserRating(context)

    def _getUser(self):
        # This is zope2 specific, not sure what to do in z3
        user_id = getattr(self, '_user_cache', ())
        if user_id is not ():
            return user_id
        if not ZOPE3:
            user = getSecurityManager().getUser()
            if user and getattr(user, 'getId', None) is not None:
                user_id = user.getId()
        else:
            # XXX: I have no idea what to do for zope3
            raise NotImplementedError
        if user_id == 'Anonymous':
            user_id = None
        self._user_cache = user_id
        return user_id

    def rate(self, rating, orig_url=None):
        """Rate an object, attempts to redirect back to the original url"""
        user = self._getUser()
        res = self.request.RESPONSE
        if self.canRate():
            self.adapted.rate(rating, user)
        else:
            self.post_rate(orig_url, 'You may not re-rate an object anonymously!')
            return
        # We set a cookie after an anonymous rating so that it's not
        # so easy to anonymously spam the ratings.
        if user is None:
            res.setCookie(self.getContentKey(), 'True', path='/')
        self.post_rate(orig_url)

    def post_rate(self, orig_url=None, message='Your rating has been saved'):
        if orig_url is not None:
            q_str = 'portal_status_message=%s' % message
            q_spacer= '?' in orig_url and '&' or '?'
            res = self.request.RESPONSE
            return res.redirect(orig_url+q_spacer+q_str)

    def getContentKey(self):
        """Create a unique string to identify the content for a cookie key,
           hopefully this will work in zope 2 and 3."""
        key = getattr(self, '_key_cache', None)
        if key:
            return key
        key = []
        if not hasattr(self.context, '__parent__'):
            subloc = None
        else:
            try:
                subloc = ISublocations(self.context.__parent__,
                            alternative=None)
            except TypeError:
                subloc = ISublocations(self.context.__parent__)

        if subloc is not None:
            for s in subloc.sublocations():
                key.append(s.__name__)
            key.insert(0, self.context.__name__)
        else:
            try:
                key.extend(self.context.getPhysicalPath())
            except AttributeError:
                pass
        if not key:
            # A cheap alternative
            key = self.KEYBASE + str(self.context)
        else:
            key = self.KEYBASE + '-'.join(key)
        self._key_cache = key
        return key

    def canRate(self):
        """Determines whether the current user is allowed to rate a piece of
           content.  Logged in users may always vote, anon users may only vote
           if they do not have the cookie indicating they have voted."""
        user = self._getUser()
        return not (user is None and
             self.request.cookies.get(self.getContentKey(), None) is not None)

    def isAuthenticated(self):
        """ """
        return self._getUser() is not None

    def userRating(self, userid=None):
        return self.adapted.userRating(userid or self._getUser())

    def _getScale(self):
        return self.adapted.scale
    scale = property(_getScale)


class MacroProvider(object):

    def _macros(self):
        return self.index.pt_macros()
    macros = property(_macros)
