import zope.configuration.fields
from zope.interface import Interface
from contentratings.interfaces import _, IRatingCategoryInfo

class ICategoryDirective(IRatingCategoryInfo):
    """Describes a rating category"""
    for_ = zope.configuration.fields.GlobalObject(
        title=_("Specifications of the object to be rated"),
        description=_("This should be a single interface or class"),
        required=True,
        )
    storage = zope.configuration.fields.GlobalObject(
        title=_("The dotted path to the storage factory"),
        description=_("This is the persistent class used for storing ratings."),
        required=False,
        )
