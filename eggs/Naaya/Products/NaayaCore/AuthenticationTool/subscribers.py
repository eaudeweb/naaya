from Products.NaayaCore.CatalogTool.interfaces import INyCatalogAware

def auto_catalog_object(event):
    obj = event.context
    if INyCatalogAware.providedBy(obj):
        catalog = obj.getSite().getCatalogTool()
        try:
            catalog.recatalogNyObject(obj)
        except:
            obj.getSite().log_current_error()
