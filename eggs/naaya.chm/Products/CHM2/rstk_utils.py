import types

from naaya.content.base.interfaces import INyContentObject
from naaya.core.zope2util import RestrictedToolkit


def patch_rstk_func(func):
    def new_func(self, *args, **kwargs):
        return func(*args, **kwargs)
    method = types.MethodType(new_func, None, RestrictedToolkit)
    setattr(RestrictedToolkit, func.__name__, method)


def has_view_name(names, REQUEST):
    """
    Checks that the accessed view name is in names and
           that the accessed object on the request is a naaya object

    This was implemented in order to check if the center portlets
    should be displayed through standard_template in the chm3 layout.
    """
    def get_view_name(REQUEST):
        try:
            return REQUEST.PUBLISHED.__name__
        except AttributeError:
            # we are probably in an error state
            # the request doesn't have the attribute 'PUBLISHED'
            return None

    def get_object_class(REQUEST):
        return type(REQUEST.PARENTS[0].aq_base)

    view_name = get_view_name(REQUEST)
    cls = get_object_class(REQUEST)
    return (view_name in names and
                INyContentObject.implementedBy(cls))


def patch_rstk():
    patch_rstk_func(has_view_name)
