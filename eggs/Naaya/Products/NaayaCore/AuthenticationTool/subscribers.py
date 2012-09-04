from Products.NaayaCore.CatalogTool.interfaces import INyCatalogAware
from naaya.core.site_logging import log_user_management_action

def auto_catalog_object(event):
    obj = event.context
    if INyCatalogAware.providedBy(obj):
        catalog = obj.getSite().getCatalogTool()
        try:
            catalog.recatalogNyObject(obj)
        except:
            obj.getSite().log_current_error()

def post_user_management_action(event):
    """ handler called after role change in user manangement """
    log_user_management_action(event.context,
                               event.manager_id,
                               event.user_id,
                               event.assigned,
                               event.unassigned)
