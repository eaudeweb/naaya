from zope.component import getAdapter, adapts, getMultiAdapter
from zope.interface import implements, Interface
from zope.traversing.interfaces import ITraversable
from Acquisition import ExplicitAcquisitionWrapper
from contentratings.interfaces import IUserRating, IEditorialRating

class user_rating(object):
    """Traversal adapter to lookup the view for a named IUserRating category.
    To demonstrate we need to make some categories and a view for those.
    First we make two categories::

        >>> from contentratings.category import RatingsCategoryFactory
        >>> category = RatingsCategoryFactory(u'Default')
        >>> category2 = RatingsCategoryFactory(u'Another', name=u'another')
        >>> from zope.interface import Interface
        >>> from zope.app.testing import ztapi
        >>> from contentratings.interfaces import IUserRating, IRatingManager
        >>> ztapi.provideAdapter((Interface,), IUserRating, category)
        >>> ztapi.provideAdapter((Interface,), IUserRating, category2,
        ...                      name=u'another')

    Then we make a default rating view::

        >>> from contentratings.browser.tests import DummyView
        >>> ztapi.provideAdapter((IRatingManager, dict), Interface,
        ...                      DummyView, name=u'ratings_view')

    Now we test that our traverser returns views on the rating managers
    for the specified category and desired interface::

        >>> from contentratings.browser.traverser import user_rating
        >>> request = {}
        >>> traverser = user_rating(my_container, request)
        >>> view = traverser.traverse('', ())
        >>> isinstance(view, DummyView)
        True
        >>> IUserRating.providedBy(view.context)
        True
        >>> IRatingManager.providedBy(view.context)
        True
        >>> view.context.name
        u''
        >>> view2 = traverser.traverse('another', ())
        >>> IUserRating.providedBy(view2.context)
        True
        >>> IRatingManager.providedBy(view2.context)
        True
        >>> isinstance(view2, DummyView)
        True
        >>> view2.context.name
        u'another'

    Looking up a bad name gives an error::

        >>> traverser.traverse('bogus', ()) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ComponentLookupError: (<zope.app.container.sample.SampleContainer object at ...>, <InterfaceClass contentratings.interfaces.IUserRating>, 'bogus')

    """
    implements(ITraversable)
    adapts(Interface)
    IFACE = IUserRating

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        """Lookup the rating category by name for the context and
        return its view"""
        manager = getAdapter(self.context, self.IFACE, name=name)
        return getMultiAdapter((manager, self.request), name=manager.view_name)

class editorial_rating(user_rating):
    """Traversal adapter to lookup the view for an IEditorialRating
    category by name"""
    IFACE = IEditorialRating
