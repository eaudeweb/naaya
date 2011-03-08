from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile

csv_email_template = EmailPageTemplateFile('emailpt/csv_import.zpt', globals())
zip_email_template = EmailPageTemplateFile('emailpt/zip_import.zpt', globals())

def skip_notifications(context):
    """This session key will be set for admins that don't want to notify
    users with their bulk modifications updates

    """
    if hasattr(context, 'REQUEST'):
        return context.REQUEST.SESSION.get('skip_notifications', False)
    return False

def handle_object_add(event):
    if not event.schema.get('_send_notifications', True):
        return

    if skip_notifications(event.context) is True:
        return

    ob = event.context
    ob.getSite().notifyFolderMaintainer(ob.aq_parent, ob)
    contributor = event.contributor
    notification_tool = ob.getSite().getNotificationTool()
    notification_tool.notify_instant(ob, contributor)

def handle_object_edit(event):
    if skip_notifications(event.context) is True:
        return

    ob = event.context
    contributor = event.contributor
    notification_tool = ob.getSite().getNotificationTool()
    notification_tool.notify_instant(ob, contributor, ob_edited=True)

def handle_csv_import(event):
    folder = event.context
    portal = folder.getSite()
    obj_titles = [folder[oid].title_or_id() for oid in event.ids]

    mail_args = {
        'ob': folder,
        'obj_titles': obj_titles,
        'item_count': len(obj_titles),
        'username': portal.REQUEST.AUTHENTICATED_USER.getUserName(),
        'datetime': portal.utShowFullDateTime(portal.utGetTodayDate()),
    }

    mail_data = csv_email_template.render_email(**mail_args)
    mail_from = portal.getEmailTool()._get_from_address()
    mail_to = portal.getMaintainersEmails(folder)
    mail_subject = mail_data['subject']
    mail_body = mail_data['body_text']

    portal.getEmailTool().sendEmail(mail_body, mail_to, mail_from,
                                    mail_subject)

def handle_zip_import(event):
    folder = event.context
    portal = folder.getSite()
    zip_contents = event.zip_contents

    mail_args = {
        'ob': folder,
        'zip_contents': zip_contents,
        'username': portal.REQUEST.AUTHENTICATED_USER.getUserName(),
        'datetime': portal.utShowFullDateTime(portal.utGetTodayDate()),
    }

    mail_data = zip_email_template.render_email(**mail_args)
    mail_from = portal.getEmailTool()._get_from_address()
    mail_to = portal.getMaintainersEmails(folder)
    mail_subject = mail_data['subject']
    mail_body = mail_data['body_text']

    portal.getEmailTool().sendEmail(mail_body, mail_to, mail_from,
                                    mail_subject)

def heartbeat_notification(site, hearthbeat):
    """notifications are delayed by 1 minute to allow for non-committed
    transactions (otherwise there's a remote chance that objects added
    or changed when heartbeat runs would be missed)"""
    when = hearthbeat.when - timedelta(minutes=1)
    site.getNotificationTool()._cron_heartbeat(when)
