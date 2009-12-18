from zope.component import getAdapters, getMultiAdapter
from contentratings.interfaces import IUserRating, IEditorialRating

class UserRatingAggregatorView(object):
    """View which combines the views of each IUserRating category for a given
    context"""
    RATING_IFACE = IUserRating
    CLASS_NAME = 'UserRatings'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_categories(self):
        """Finds all named rating categories for the object matching
        the classes RATING_IFACE, and returns them in order"""
        adapters = getAdapters((self.context,), self.RATING_IFACE)
        return sorted((a for n, a in adapters), key=lambda x: x.order)

    def _get_view(self, manager):
        return getMultiAdapter((manager, self.request), name=manager.view_name)

    def __call__(self):
        """Returns a simple div containing all of the ordered rating category
        views"""
        categories = self._get_categories()
        rendered = list(v for v in (self._get_view(m)() for m in categories)
                                                            if v.strip())
        if not rendered:
            return u''
        return u'<div class="%s">%s</div>'%(self.CLASS_NAME,
                                            '\n'.join(rendered))


class EditorialRatingAggregatorView(UserRatingAggregatorView):
    """View which combines the views of each IEditorialRating category
    for a given context"""
    RATING_IFACE = IEditorialRating
    CLASS_NAME = 'EditorialRatings'
