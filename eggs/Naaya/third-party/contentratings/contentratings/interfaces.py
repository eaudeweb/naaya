from zope.interface import Interface, Attribute, directlyProvides
from zope.interface.interfaces import IInterface
from zope.annotation.interfaces import IAnnotatable
from zope.app.component.vocabulary import InterfacesVocabulary

from zope.schema import Float
from zope.schema import Int
from zope.schema import ASCII
from zope.schema import Datetime
from zope.schema import Text
from zope.schema import TextLine
from zope.i18nmessageid import MessageFactory
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
_ = MessageFactory('contentratings')

class IEditorRatable(IAnnotatable):
    """Marker interface that promises that an implementing object may be
    rated by an editor using the IEditorialRating interface.
    """

class IUserRatable(IAnnotatable):
    """Marker interface that promises that an implementing object may be
    rated by users using the IUserRating interface.
    """

class IRatingStorage(Interface):
    """A marker interface indicating that an object is used
    to store ratings in an annotation"""

class IRating(Interface):
    """An object representing a user rating, the rating attributes
    are immutable.  The object itself should be a Float, though there
    is no IFloat to be inherited from other than the schema field."""

    userid = ASCII(
        title=_(u"User Id"),
        description=_(u"The id of the user who set the rating"),
        required=False,
        readonly=True,
        )

    timestamp = Datetime(
        title=_(u"Time Stamp"),
        description=_(u"The date and time the rating was made (UTC)"),
        required=True,
        readonly=True
        )


class IRatingType(IInterface):
    """A marker indicating that an interface is a type of rating storage"""


class IEditorialRating(Interface):
    """Set a single global rating.
    """

    rating = Float(
        title=_(u"Rating"),
        description=_(u"The rating of the current object"),
        required=False
        )

    scale = Attribute("Deprecated restriction on the maximum value")

directlyProvides(IEditorialRating, IRatingType)

class IUserRating(Interface):
    """A rating class that allows users to set and adjust their ratings of
       content.
    """
    def rate(rating, username=None, session_key=None):
        """Rate the current object with `rating`.  Optionally rate the
           content anonymously if username is None.  If no username is
           passed a unique session key can be passed, which can be
           used by views to check for repeat anonymous ratings.
           Returns the created IRating object.
        """

    def userRating(username=None):
        """Return the IRating for a given username.

           Returns None if the user has not yet rated the object.
           Returns the average of anonymous ratings if the username is None.
        """

    def remove_rating(username):
        """Removes the rating for the specified user"""

    def all_user_ratings(include_anon=False):
        """Returns an iterable of all the contained IRatings objects
        in no particular order.  This optionally includes anonymous
        ratings.
        """

    def last_anon_rating(session_key):
        """Returns the timestamp indicating the last time the content was
        rated anonymously by the user with the given session_key.  Can be
        used by views to restrict frequency of anonymous voting.
        """

    averageRating = Attribute(u"Mean of all ratings")
    most_recent = Attribute(u"The most recently added IRating object")
    all_raters = Attribute(u"An iterable of all the userids which have rated "
                           u"the object")
    numberOfRatings = Attribute(u"Number of ratings")

    # BBB: deprecated properties
    scale = Attribute("Deprecated restriction on the maximum value")
directlyProvides(IUserRating, IRatingType)


class IObjectRatedEvent(IObjectModifiedEvent):
    """An event that is emitted when an object is rated by a user"""
    rating = Attribute("The IRating set on the object")
    category = Attribute("The category in which this rating was set")

#BBB
class IObjectUserRatedEvent(IObjectRatedEvent):
    """An event that is emitted when an object is rated by a user"""

#BBB
class IObjectEditorRatedEvent(IObjectRatedEvent):
    """An event that is emitted when an object is rated by an editor"""

class IRatingStorageMigrator(Interface):
    """Class for migrating the rating storage from one form to another"""

class IRatingCategoryInfo(Interface):
    """Describes the schema of a ratings category"""
    name = TextLine(
        title=_(u"Category Id"),
        description=_(u"Unique Id for this rating category"),
        required=False,
        default=u'',
        readonly=True,
        )

    title = TextLine(
        title=_(u"Title"),
        description=_(u"The displayed title of this ratings category, "
                      u"keep this concise"),
        required=True,
        )

    description = TextLine(
        title=_(u"Description"),
        description=_("The description of the category for display in the "
                      "user interface."),
        default=u'',
        required=False,
        )

    # This will eventually be a Choice field,
    # with a vocabulary of views
    view_name = TextLine(
        title=_(u"View"),
        description=_(u"Select the view for this category"),
        default=u'rating_view',
        required=False,
        )

    read_expr = TextLine(
        title=_(u"Read Expression"),
        description=_(u"A TALES expression used to determine whether viewing "
                      u"the rating is allowed.  Leave blank to always allow."),
        required=False,
        )

    write_expr = TextLine(
        title=_(u"Write Expression"),
        description=_(u"A TALES expression used to determine whether setting "
                      u"the rating is allowed.  Leave blank to always allow."),
        required=False,
        )

    order = Int(
        title=_(u"Order"),
        description=_("The relative order in which the category should "
                      "appear."),
        required=False,
        default=100,
        )


class IRatingCategory(IRatingCategoryInfo):
    """Defines the additional attributes of a RatingCategory implementation"""
    __name__ = Attribute(u"An alias for name")
    storage = Attribute(u"A factory for generating persistable rating storages")
    read = Attribute(u"The compiled expression which is used to determine "
                     u"if viewing the rating is allowed")
    write = Attribute(u"The compiled expression which is used to determine "
                      u"if setting the rating is allowed")


class IRatingManager(Interface):
    """The adapter responsible for providing the rating interface
    to the views"""

    context = Attribute(u"The object to be rated")

    title = Attribute(u"The title")
    description = Attribute(u"The description")
    order = Attribute(u"The order of this category relative to others")
    name = Attribute(u"The name of the rating category")
    userid = Attribute(u"The current user id, for convenience")
    can_read = Attribute(u"Indicates whether the rating can be viewed")
    can_write = Attribute(u"Indicates whether the rating can be set")
    view_name = Attribute(u"The name of the rating view")
    storage = Attribute(u"The rating storage")

# The vocabulary of interfaces providing IRatingType
class RatingTypeVocabulary(InterfacesVocabulary):
    interface = IRatingType
