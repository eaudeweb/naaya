from zope.interface import Interface, alsoProvides
from zope.configuration import fields
from zope.app.i18n import ZopeMessageFactory as _
from zope.component import getGlobalSiteManager

from interfaces import IDumpReader
from main import get_reader

class IReaderDirective(Interface):
    """ ZCML Directive that registers a naaya.ldapdump reader """
    path = fields.Path(
        title=_("Path"),
        description=_("Path to configuration file for this dump"),
        required=True,
    )

def register_reader(_context, path, **kwargs):
    reader = get_reader(path)
    alsoProvides(reader, IDumpReader)
    getGlobalSiteManager().registerUtility(reader)
