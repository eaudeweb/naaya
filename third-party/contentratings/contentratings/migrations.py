from zope.component import adapts
from zope.interface import implements
from BTrees.OOBTree import OOBTree
from contentratings.storage import UserRatingStorage, EditorialRatingStorage
from contentratings.interfaces import IRatingStorageMigrator

class UserRatingMigrator(object):
    """Converts converts an OOBTree based rating store into
    the new UserRating storage"""
    implements(IRatingStorageMigrator)
    adapts(OOBTree, UserRatingStorage)

    def __init__(self, orig, new):
        self.orig = orig
        self.new = new

    def migrate(self):
        """Converts the older BTree storage into the new
        object based storage"""
        orig = self.orig
        new = self.new
        avg = new._anon_average = orig['anon_average']
        if orig.has_key('anon_ratings'):
            # We have the original anonymous rating list
            for rating in orig['anon_ratings']:
                new.rate(rating)
        elif orig.has_key('anon_count'):
            # Add bogus entries with the average value for each
            # anonymous rating
            for x in xrange(orig['anon_count']):
                new.rate(avg)
        # transfer all the user ratings
        for userid, rating in orig['ratings'].iteritems():
            new.rate(rating, userid)
        # returns our mutated storage object
        return new

class EditorialRatingMigrator(UserRatingMigrator):
    """Converts converts the simple float based rating store into
    the new EditorialRating storage"""
    adapts(float, EditorialRatingStorage)

    def migrate(self):
        """Converts the older simple float into the new
        object based storage"""
        self.new.rating = self.orig
        return self.new
