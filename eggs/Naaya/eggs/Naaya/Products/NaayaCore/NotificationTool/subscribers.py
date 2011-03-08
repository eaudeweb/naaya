from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile

import utils

csv_email_template = EmailPageTemplateFile('emailpt/csv_import.zpt', globals())
zip_email_template = EmailPageTemplateFile('emailpt/zip_import.zpt', globals())

def check_skip_notifications(subscriber):
    """This session key will be set for admins that don't want to notify
    users with their bulk modifications updates

    """
    def wrapper(event):
        if (hasattr(event.context, 'REQUEST') and
            hasattr(event.context.REQUEST, 'SESSION') and
            event.context.REQUEST.SESSION.get('skip_notifications', False) is
            True):
            return
        return subscriber(event)
    return wrapper

@check_skip_notifications
def handle_object_add(event):
    if not event.schema.get('_send_notifications', True):
        return

    ob = event.context
    ob.getSite().notifyFolderMaintainer(ob.aq_parent, ob)
    contributor = event.contributor
    notification_tool = ob.getSite().getNotificationTool()
    notification_tool.notify_instant(ob, contributor)

@check_skip_notifications
def handle_object_edit(event):
    ob = event.context
    contributor = event.contributor
    notification_tool = ob.getSite().getNotificationTool()
    notification_tool.notify_instant(ob, contributor, ob_edited=True)

@check_skip_notifications
def handle_csv_import(event):
    """ Send instant notification when a csv is imported to a folder"""

    portal = event.context.getSite()
    obj_titles = [event.context[oid].title_or_id() for oid in event.ids]

    subscriber_data_default = {
        'username': portal.REQUEST.AUTHENTICATED_USER.getUserName(),
        'obj_titles': obj_titles,
        'item_count': len(obj_titles),
        'datetime': portal.utShowFullDateTime(portal.utGetTodayDate()),
    }

    import_subscriber(event, subscriber_data_default, csv_email_template)

@check_skip_notifications
def handle_zip_import(event):
    """Send instant notification when an zip is imported to a folder"""

    portal = event.context.getSite()
    subscriber_data_default = {
        'username': portal.REQUEST.AUTHENTICATED_USER.getUserName(),
        'zip_contents': event.zip_contents,
        'datetime': portal.utShowFullDateTime(portal.utGetTodayDate())
    }

    import_subscriber(event, subscriber_data_default, zip_email_template)


def send_notifications_for_event(event, subscriber_data_default, template):
    """Send notifications to site maintainers and subscribers"""

    folder = event.context
    portal = folder.getSite()
    notification_tool = portal.getNotificationTool()

    subscribers_data = {}
    maintainers_data = {}

    #Get maintainers
    maintainers = portal.getMaintainersEmails(folder)
    for email in maintainers:
        data = dict(subscriber_data_default)
        data.update({
            'ob': folder,
            'here': notification_tool,
        })
        maintainers_data[email] = data

    #Get subscribers
    if notification_tool.config['enable_instant'] is True:
        subscribers_data = utils.get_subscribers_data(notification_tool,
            folder, **subscriber_data_default)

    subscribers_data.update(maintainers_data)
    notification_tool._send_notifications(subscribers_data,
                                          template.render_email)

def heartbeat_notification(site, hearthbeat):
    """notifications are delayed by 1 minute to allow for non-committed
    transactions (otherwise there's a remote chance that objects added
    or changed when heartbeat runs would be missed)"""

    when = hearthbeat.when - timedelta(minutes=1)
    site.getNotificationTool()._cron_heartbeat(when)
