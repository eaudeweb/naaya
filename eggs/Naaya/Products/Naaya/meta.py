from zope.interface import Interface
from zope.configuration.fields import GlobalObject, GlobalInterface
from zope.schema import TextLine
from zope.security.zcml import Permission
from zope.app.i18n import ZopeMessageFactory as _
from Products.Five.browser import BrowserView, metaconfigure


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
        def __call__(self):
            context = self.aq_parent
            return handler(context, self.request)

    metaconfigure.page(_context, name, permission, for_, class_=SimpleView)
