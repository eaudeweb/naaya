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
    user_id_or_group = event.user_id
    if event.is_group:
        user_id_or_group = 'group: %s' % event.user_id
    log_user_management_action(event.context,
                               event.manager_id,
                               user_id_or_group,
                               event.assigned,
                               event.unassigned)
    if event.send_mail:
        auth_tool = event.context.getAuthenticationTool()
        notif_tool = event.context.getNotificationTool()
        if event.is_group:
            for user_source in auth_tool.getSources():
                user_ids = user_source.group_member_ids(event.user_id)
                if user_ids:
                    break
            for user_id in user_ids:
                email = auth_tool.getUsersEmails([user_id])[0]
                full_name = auth_tool.getUsersFullNames([user_id])[0]
                notif_tool.notify_account_modification(email, event.context,
                    new_roles=event.assigned, removed_roles=event.unassigned,
                    username=full_name)
        else:
           email = auth_tool.getUsersEmails([event.user_id])[0]
           full_name = auth_tool.getUsersFullNames([event.user_id])[0]
           notif_tool.notify_account_modification(email, event.context,
                    new_roles=event.assigned, removed_roles=event.unassigned,
                    username=full_name)
