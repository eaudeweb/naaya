from datetime import datetime, timedelta
from zope.interface import Interface, implements
from zope.component import queryUtility, queryMultiAdapter
from zope.traversing.browser.interfaces import IAbsoluteURL
from contentratings.browser.interfaces import IAnonymousSession
from contentratings.browser.interfaces import IRatingView
from contentratings.interfaces import _
from zope.schema.interfaces import IVocabularyTokenized
try:
    from Products.statusmessages.interfaces import IStatusMessage
except ImportError:
    # No Plone
    class IStatusMessage(Interface):
        pass

class BasicEditorialRatingView(object):
    """A basic view for applying and removing user ratings.  Expects
    its context to be an IRatingManager providing IEditorialRating."""
    vocab_name = 'contentratings.browser.base_vocabs.five_star_vocab'
    traversal_name = 'EditorialRating'
    implements(IRatingView)

    def __init__(self, context, request):
        """We implement this to make the tests happy"""
        self.context = context
        self.request = request

    @property
    def vocabulary(self):
        """Get te named vocabulary for vaildation"""
        return queryUtility(IVocabularyTokenized, self.vocab_name)

    @property
    def content_url(self):
        """Returns the content url, try to make Zope 2 and 3 happy"""
        # context.context is the content being rated
        context = self.context.context
        # Use Zope 3 mechanism if possible
        url = queryMultiAdapter((context, self.request),
                                IAbsoluteURL)
        # Fallback on Zope 2's OFS.Traversible
        if url is None and hasattr(context, 'absolute_url'):
            url = context.absolute_url()
        return url

    def rate(self, value, redirect=True):
        """Rate the content.  Enforce vocabulary values.
        """
        assert int(value) in self.vocabulary
        msg = _(u'The rating has been changed')

        self.context.rating = value
        return self._redirect(redirect, msg=msg)

    def _setMessage(self, msg):
        """Attempt to send a message to the user. Plone only for now."""
        sm = IStatusMessage(self.request, alternate=None)
        if sm is not None:
            sm.addStatusMessage(msg, type='info')

    def _redirect(self, redirect, msg=None):
        """Redirect the user to a specified url and set a status message if
        desired.  Use the content url if the url is not specified.
        """
        if redirect:
            url = self.request.get('HTTP_REFERER', self.content_url)
            redirect = redirect == True and url or redirect
            if msg:
                self._setMessage(msg)
            self.request.response.redirect(redirect)
        return msg


class BasicUserRatingView(BasicEditorialRatingView):
    """A basic view for applying and removing user ratings.  Expects
    its context to be an IRatingManager providing IUserRating."""

    # 1 Year rating timeout
    ANON_TIMEOUT = timedelta(365)
    traversal_name = 'UserRating'

    @property
    def _session_key(self):
        """Lookup the anonymous session key"""
        ses_util = queryUtility(IAnonymousSession)
        if ses_util is not None:
            return ses_util.get_anon_key(self.request)

    @property
    def can_rate(self):
        """A user can rate if the rating manager says so.  Make sure
        anonymous users cannot repeatedly rate the same content by using
        the threshold time and a session id"""
        context = self.context
        userid = context.userid
        # check the category write expression
        if not context.can_write:
            return False
        elif userid is None:
            key = self._session_key
            if key is not None:
                # If another rating was made under this session, don't allow
                # another rating unless enough time has passed.  We need to use
                # the storage directly because we need this info, even if the
                # user can't view other ratings.
                last_rating = context.storage.last_anon_rating(key)
                if last_rating and \
                       (datetime.utcnow() - last_rating) <= self.ANON_TIMEOUT:
                    return False
        return True

    def rate(self, value, redirect=True):
        """Rate the content.  Enforce vocabulary values.
        """
        assert int(value) in self.vocabulary
        context = self.context
        userid = context.userid
        msg = _(u'You have changed your rating')
        if userid is None and not self.can_rate:
            return self._redirect(redirect,
                                  msg=_(u'You have already rated this '
                                        u'item, and cannot change your '
                                        u'rating unless you log in.'))
        elif userid is None:
            # rate the object passing in the session id
            context.rate(value, session_key=self._session_key)
        else:
            context.rate(value, userid)
        return self._redirect(redirect, msg=msg)

    def remove_rating(self, redirect=True):
        """Remove the rating for the current user"""
        context = self.context
        userid = context.userid
        if userid:
            context.remove_rating(userid)
        return self._redirect(redirect, msg=_(u'You have removed your rating'))


    @property
    def current_rating(self):
        """Return the logged in user's currently set rating regardless of
        security settings.  Users should always be able to see their own
        rating."""
        context = self.context
        userid = context.userid
        # go directly to the storage to bypass security
        return userid and context.storage.userRating(userid)

class SmallStarUserRating(BasicUserRatingView):
    """A view that specifies small stars"""
    star_size = 12 # px

class ThreeStarUserRating(SmallStarUserRating):
    """A view that specifies small stars"""
    vocab_name='contentratings.browser.base_vocabs.three_star_vocab'
