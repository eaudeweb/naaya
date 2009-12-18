from zope.interface import Interface
from zope.interface import Attribute

class IEditorialRatingView(Interface):
    """
    """
    rating = Attribute(u"Editor Rating")
