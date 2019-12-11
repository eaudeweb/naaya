from __future__ import absolute_import
from .interfaces import IDumpReader
from .main import get_reader
from zope.component import getGlobalSiteManager
from zope.configuration import fields
from zope.interface import Interface, alsoProvides

try:
    from zope.app.i18n import ZopeMessageFactory as _
except ImportError:
    from zope.i18nmessageid import ZopeMessageFactory as _



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
