import logging
from datetime import timedelta
from naaya.core.utils import cooldown
from naaya.core.zope2util import ofs_path
from constants import NAAYAGLOSSARY_CENTRE_METATYPE

log = logging.getLogger('Products.NaayaGlossary.subscribers')

def sync_on_heartbeat(site, hearthbeat):
    if cooldown('glossary sync %r' % ofs_path(site), timedelta(days=7)):
        return

    for glossary in site.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
        glossary.manage_perform_sync()

def add_item_to_glossary_catalog(item, event):
    try:
        catalog = item.getGlossaryCatalog()
        catalog.catalog_object(item)
    except:
        log.exception("Failed to add %r to glossary catalog", item)

def remove_item_from_glossary_catalog(item, event):
    try:
        catalog = item.getGlossaryCatalog()
        item_path = ofs_path(item)
        if catalog.getrid(item_path) is not None:
            catalog.uncatalog_object(item_path)
    except:
        log.exception("Failed to remove %r from glossary catalog", item)
