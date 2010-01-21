from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile

csv_email_template = EmailPageTemplateFile('emailpt/csv_import.zpt', globals())

def handle_object_add(event):
    if not event.schema.get('_send_notifications', True):
        return
    ob = event.context
    ob.getSite().notifyFolderMaintainer(ob.aq_parent, ob)
    contributor = event.contributor
    notification_tool = ob.getSite().getNotificationTool()
    notification_tool.notify_instant(ob, contributor)

def handle_object_edit(event):
    ob = event.context
    contributor = event.contributor
    notification_tool = ob.getSite().getNotificationTool()
    notification_tool.notify_instant(ob, contributor, ob_edited=True)

def handle_csv_import(event):
    folder = event.context
    portal = folder.getSite()
    obj_titles = [folder[oid].title_or_id() for oid in event.ids]

    mail_args = {'ob': folder,
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

    portal.getEmailTool().sendEmail(mail_body, mail_to, mail_from, mail_subject)

def update_subscriptions_after_move(event):
    """ object was renamed; update subscription list if needed """
    old_site_path = event.old_site_path
    new_site_path = event.new_site_path
    notification_tool = event.context.getSite().getNotificationTool()

    for s in notification_tool.list_subscriptions():
        if s.location == old_site_path:
            notification_tool.remove_subscription(s.user_id, old_site_path,
                                                  s.notif_type, s.lang)
            notification_tool.add_subscription(s.user_id, new_site_path,
                                               s.notif_type, s.lang)
