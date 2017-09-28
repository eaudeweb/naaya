from zope.interface import Interface
from zope.configuration.fields import GlobalObject, GlobalInterface, Bool
from zope.schema import TextLine
from zope.security.zcml import Permission
from zope.app.i18n import ZopeMessageFactory as _
from Products.Five.browser import BrowserView, metaconfigure
from naaya.component import bundles
from naaya.core.interfaces import IRstkMethod


class INaayaCallDirective(Interface):
    """ Call something """
    factory = GlobalObject(
        title=_("Factory"),
        description=_("Call the given factory. That's all we do. Simple."),
        required=True,
    )


def call_directive(_context, factory):
    factory()


class INaayaSimpleViewDirective(Interface):
    """ Define a simple zope3 view """
    for_ = GlobalInterface(
        title=u"The interface this view is for.",
        required=True,
        )
    name = TextLine(
        title=u"The name of the view.",
        description=u"The name shows up in URLs/paths. For example 'foo'.",
        required=True,
        )
    handler = GlobalObject(
        title=_("Handler"),
        description=_("Function that handles the view."),
        required=True,
    )
    permission = Permission(
        title=u"Permission",
        description=u"The permission needed to use the view.",
        required=False,
        )


_default_permission = 'zope.Public'

def simple_view_directive(_context, handler, for_, name,
                          permission=_default_permission):
    class SimpleView(BrowserView):
        def __call__(self, **kwargs):
            context = self.aq_parent
            return handler(context, self.request, **kwargs)

    metaconfigure.page(_context, name, permission, for_, class_=SimpleView)


class INaayaRstkMethodDirective(Interface):
    """ Register a RSTK method """
    handler = GlobalObject(
        title=_("Implementation of the method"),
        required=True,
    )
    name = TextLine(
        title=u"Name of method (defaults to __name__ attribute of handler)",
        required=False,
        )
    context = Bool(
        title=u"Send context as first argument",
        required=False,
    )
    bundle = TextLine(
        title=u"Bundle to register the method (default 'Naaya')",
        required=False,
        )
    getattrPatch = Bool(
        title=u"Backwards-compatibility patch for old getattr-style access",
        required=False,
    )


def rstk_method_directive(_context, handler, name=None,
                          context=False, bundle='Naaya', getattrPatch=False):
    if name is None:
        name = handler.__name__

    if not context:
        orig_handler = handler
        handler = lambda ctx, *args, **kwargs: orig_handler(*args, **kwargs)

    bundles.get(bundle).registerUtility(handler, IRstkMethod, name)

    if getattrPatch:
        import warnings
        from naaya.core.zope2util import RestrictedToolkit
        msg = ("RestrictedToolkit method %(name)r should be accessed as "
               "rstk[%(name)r] instead of rstk.%(name)s" % {'name': name})
        to_warn = [1]

        def compatibility_handler(*args, **kwargs):
            if to_warn:
                warnings.warn(msg, DeprecationWarning)
                to_warn[:] = []

            return handler(*args, **kwargs)

        setattr(RestrictedToolkit, name, compatibility_handler)
