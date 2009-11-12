from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile


csv_email_template = EmailPageTemplateFile('emailpt/csv_import.zpt', globals())

def handler_object_added(event):
    if event.schema.get('_send_notifications', True):
        ob = event.context
        ob.getSite().notifyFolderMaintainer(ob.aq_parent, ob)

def handler_csv_import(event):
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
    mail_from = portal.get_portal_mail_address()
    mail_to = portal.getMaintainersEmails(folder)
    mail_subject = mail_data['subject']
    mail_body = mail_data['body_text']

    portal.getEmailTool().sendEmail(mail_body, mail_to, mail_from, mail_subject)
