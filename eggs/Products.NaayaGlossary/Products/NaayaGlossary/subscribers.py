import logging
from naaya.core.zope2util import ofs_path

log = logging.getLogger('Products.NaayaGlossary.subscribers')

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
