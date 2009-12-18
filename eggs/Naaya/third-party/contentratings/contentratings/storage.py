from datetime import datetime
from itertools import chain
from zope.interface import implements
from zope.app.container.contained import Contained
from zope.event import notify
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from contentratings.rating import Rating
from contentratings.interfaces import (
    IEditorialRating,
    IUserRating,
    IRatingStorage)

SINGLEKEY = "contentrating.singlerating"

class UserRatingStorage(Contained, Persistent):
    """BTree-based storage for user ratings, keeps a running
    statistics tally for efficiency."""
    implements(IUserRating, IRatingStorage)

    _average = 0.0
    _anon_average = 0.0
    _most_recent = None
    # BBB
    scale = 5

    def __init__(self):
        """Setup our data structures"""
        self._anon_ratings = IOBTree()
        self._ratings = OOBTree()
        self._sessions = OOBTree()

    def rate(self, rating, username=None, session_key=None):
        """Set a rating for a particular user"""
        # We keep a running average for efficiency, we need to
        # have the current statistics to do so
        orig_total = self._average * self.numberOfRatings
        orig_rating = self._ratings.get(username, 0.0)
        rating = Rating(rating, username)
        if username:
            self._ratings[username] = rating
        else:
            # For anonymous users, we use a sequential key, which
            # may lead to conflicts.  There's probably a better way
            anon_total = self._anon_average * self._anon_count
            key = len(self._anon_ratings) + 1
            self._anon_ratings[key] = rating
            self._anon_average = (anon_total + rating)/self._anon_count
            # If a session key was passed in for an anonymous user
            # store it with a datestamp
            if session_key:
                self._sessions[session_key] = datetime.utcnow()
        # Calculate the updated average
        self._average = (orig_total + rating - orig_rating)/self.numberOfRatings
        # Mark this new rating as the most recent
        self._most_recent = rating
        return rating

    def userRating(self, username=None):
        """Retreive the rating for the specified user, or the average
        anonymous rating if no user is specified"""
        if username is not None:
            return self._ratings.get(username, None)
        else:
            if self._anon_count:
                return Rating(self._anon_average)
            else:
                return None

    def remove_rating(self, username):
        """Remove the rating for a given user"""
        orig_total = self._average * self.numberOfRatings
        rating = self._ratings[username]
        del self._ratings[username]
        # Since we want to keep track of the most recent rating, we
        # need to replace it with the second most recent if the most
        # recent was deleted
        if rating is self.most_recent:
            ordered = sorted(self.all_user_ratings(True),
                             key=lambda x: x.timestamp)
            if ordered:
                self._most_recent = ordered[-1]
            else:
                self._most_recent = None
        # Update the average
        self._average = float(self.numberOfRatings and
                                 (orig_total - rating)/self.numberOfRatings)

    @property
    def _anon_count(self):
        return len(self._anon_ratings)

    @property
    def most_recent(self):
        return self._most_recent

    def all_user_ratings(self, include_anon=False):
        ratings = self._ratings.values()
        if include_anon:
            ratings = chain(ratings, self._anon_ratings.values())
        return ratings

    def all_raters(self):
        return self._ratings.keys()

    @property
    def numberOfRatings(self):
        return len(self._ratings) + self._anon_count

    @property
    def averageRating(self):
        return self._average

    def last_anon_rating(self, session_key):
        """Returns a timestamp indicating the last time the anonymous user
        with the given session_key rated the object."""
        return self._sessions.get(session_key, None)

# This is mainly here for BBB.  The rating category mechanism with the
# standard UserRatingStorage can cover this usecase using well
# defined read/write expressions
class EditorialRatingStorage(Contained, Persistent):
    implements(IEditorialRating, IRatingStorage)
    # BBB
    scale = 5
    annotation_key = SINGLEKEY

    def _setRating(self, rating):
        self._rating = Rating(rating)

    def _getRating(self):
        return getattr(self, '_rating', None)
    rating = property(fget=_getRating, fset=_setRating)


