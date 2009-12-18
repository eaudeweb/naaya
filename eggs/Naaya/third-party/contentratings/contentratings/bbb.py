from contentratings.category import RatingsCategoryFactory, BASE_KEY
from contentratings.interfaces import _
from contentratings.permissions import (
    EditorRate,
    ViewEditorialRating,
    UserRate,
    ViewUserRating,
    )
from contentratings.storage import EditorialRatingStorage, SINGLEKEY

# A Plone-y permission expression since these classes are just for BBB with
# Plone products
PERM_EXPR = ("python:getattr(getattr(context, 'portal_membership' ,None),"
                                 " 'checkPermission', lambda *x: True)('%s',"
                                                                    " context)")
EditorialRatingCat = RatingsCategoryFactory(_(u'Editor Rating'),
                                       read_expr=PERM_EXPR%ViewEditorialRating,
                                       write_expr=PERM_EXPR%EditorRate,
                                       storage=EditorialRatingStorage)
UserRatingCat = RatingsCategoryFactory(_(u'User Rating'),
                                       read_expr=PERM_EXPR%ViewUserRating,
                                       write_expr=PERM_EXPR%UserRate)

# BBB: We fake a class for these categories where the key can be
# overridden by sub-classes, hopefully this is all anyone customized.
class UserRating(object):
    """A dummy class which actually returns the result of calling the
    category factory, for BBB."""
    category = UserRatingCat
    key = BASE_KEY

    def __new__(cls, context):
        self = cls
        self.category.key = self.key
        # instantiate the category
        return self.category(context)

class EditorialRating(UserRating):
    category = EditorialRatingCat
    key = SINGLEKEY
