from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.app.i18n import ZopeMessageFactory as _

class INaayaCallDirective(Interface):
    """ Call something """
    factory = GlobalObject(
        title=_("Factory"),
        description=_("Call the given factory. That's all we do. Simple."),
        required=True,
    )

def call_directive(_context, factory):
    factory()
