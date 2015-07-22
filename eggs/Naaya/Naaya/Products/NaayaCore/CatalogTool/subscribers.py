from zope.component import adapter
from zope.app.container.interfaces import (IObjectAddedEvent,
                                           IObjectRemovedEvent)

from interfaces import INyCatalogAware

def physical_path(obj):
    return '/'.join(obj.getPhysicalPath())

@adapter(INyCatalogAware, IObjectAddedEvent)
def auto_catalog_object(obj, event):
    catalog = obj.getSite().getCatalogTool()
    try:
        catalog.catalog_object(obj, physical_path(obj))
    except:
        obj.getSite().log_current_error()

@adapter(INyCatalogAware, IObjectRemovedEvent)
def auto_uncatalog_object(obj, event):
    catalog = obj.getSite().getCatalogTool()
    try:
        catalog.uncatalog_object(physical_path(obj))
    except:
        obj.getSite().log_current_error()
