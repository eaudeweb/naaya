from zope.interface import Interface
from zope.configuration import fields
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope')

import logging

log = logging.getLogger('edw.circaimport')

class IRootPathDirective(Interface):
    path = fields.Path(
        title=_("Path"),
        description=_("Path prefix where to look for CIRCA zip files."),
        required=True,
    )

def register_root_path(_context, path, **kwargs):
    log.info("CIRCA import folder: %r", path)
    from . import ui
    ui.upload_prefix = path
