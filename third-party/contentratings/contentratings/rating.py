from datetime import datetime
from persistent import Persistent
from zope.interface import implements
from zope.deferredimport import deprecatedFrom
from contentratings.interfaces import IRating

_marker = []

deprecatedFrom('Rating categories should be created using the category '
               'factory or the zcml directive.  The UserRating and '
               'EditorialRating adapters are now deprecated and may behave '
               'differently.',
               'contentratings.bbb', 'UserRating', 'EditorialRating')

class NPRating(float):
    """A non-persistent IRating object, for storages which store
    outside the ZODB, or which have no desire to annotate/mutate
    ratings."""
    implements(IRating)

    # No security on this
    __allow_access_to_unprotected_subobjects__ = True

    def __new__(cls, rating, userid=None):
        self = float.__new__(cls, rating)
        self.userid = userid
        self.timestamp = datetime.utcnow()
        return self

    def __repr__(self):
        return '<%s %r by %r on %s>' %(self.__class__.__name__, float(self),
                                       self.userid, self.timestamp.isoformat())

    def __str__(self):
        return str(float(self))


# We can't inherit float and Persistent, because of conflicting C bases, so
# we duck-type
class Rating(Persistent):
    """Behaves like a float with some extra attributes"""
    implements(IRating)

    # No security on this
    __allow_access_to_unprotected_subobjects__ = True

    def __init__(self, rating, userid=None):
        self._rating = float(rating)
        self.userid = userid
        self.timestamp = datetime.utcnow()

    __repr__ = NPRating.__repr__.im_func
    __str__ = NPRating.__str__.im_func

    def __add__(self, other):
        """Make sure we can add ratings"""
        return float(self) + float(other)

# Apply float-like behaviors to our persistent rating class by adding
# special methods from float to obtain thorough duck-typing
def _float_proxy(name):
    def floatish(self, *args, **kwargs):
        return getattr(self._rating, name)(*args, **kwargs)
    # make sure our methods get proper names and doc strings
    floatish.__doc__ = getattr(float, name).__doc__
    floatish.__name__ = name
    return floatish

for fname in dir(float()):
    func = getattr(float(), fname)
    # don't overwrite anything
    if callable(func) and fname not in dir(Rating):
        setattr(Rating, fname, _float_proxy(fname))
