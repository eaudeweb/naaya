def auto_catalog_object(event):
    obj = event.context
    catalog = obj.getSite().getCatalogTool()
    try:
        catalog.recatalogNyObject(obj)
    except:
        obj.getSite().log_current_error()
