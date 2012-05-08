from Products.Naaya.interfaces import INySite

def auto_catalog_object(event):
    obj = event.context
    if not INySite.providedBy(obj):
        catalog = obj.getSite().getCatalogTool()
        try:
            catalog.recatalogNyObject(obj)
        except:
            obj.getSite().log_current_error()
