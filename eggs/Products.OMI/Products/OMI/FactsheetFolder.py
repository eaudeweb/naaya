# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ZCatalog.ZCatalog import manage_addZCatalog
#from Products.MailHost.MailHost import MailHost, manage_addMailHost
#from Products.ZTinyMCE.TinyMCE import manage_addZTinyMCE       --- no longer needed (served from zip)

from constants import *
from utilities import *
from Factsheet import manage_addFactsheet_html

#------------------------------------------------------------------------------

manage_addFactsheetFolder_html = PageTemplateFile('zpt/folder', globals())

def loadCatalogueMetadata(catalogue):
    # create columns
    catalogue.addColumn('id')
    catalogue.addColumn('title')
    catalogue.addColumn('meta_type')
    catalogue.addColumn('bobobase_modification_time')

    # create indexes
    catalogue.addIndex('id', 'FieldIndex')

    catalogue.manage_addIndex('model_keywords', 'TextIndexNG3', extra={'default_encoding': 'utf-8', 'splitter_casefolding': True})
    for field in searchable_lists:
        catalogue.addIndex(field, 'KeywordIndex')

#------------------------------------------------------------------------------

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

def manage_addFactsheetFolder(self, title, administrator_email, REQUEST=None):
    "Method for adding a Factsheet container"
    if not title:
        raise ValueError('Name of Folder is mandatory!')
    if not administrator_email:
        raise ValueError('The administrative email is mandatory!')
    if not email_expr.match(administrator_email):
        raise ValueError('Please enter a valid email address!')
    id = slugify(title)
    newFactsheetFolder = FactsheetFolder(id, title, administrator_email)
    self._setObject(id, newFactsheetFolder)
    folder = self._getOb(id)
    manage_addZCatalog(folder, id='catalogue', title='Models catalogue')
    catalogue = folder._getOb('catalogue')
    loadCatalogueMetadata(catalogue)

    #Check for and add a MailHost object
    #ob = getattr(folder, MAILHOST, None)
    #if not ob:
        #manage_addMailHost(self, id=MAILHOST, title=MAILHOST, smtp_host='localhost', smtp_port=25)

    # Alternative way to create a TinyMCE object and to set the configuration
    #manage_addZTinyMCE(folder, id='TinyMCE')
    #TinyMCE = folder._getOb('TinyMCE')
    #conf_file=getattr(TinyMCE, 'advanced.conf')
    #conf_file.manage_saveConfiguration(ZTinyMCE_CONFIGURATION, 'Example configuration')

    return self.manage_main(self, REQUEST)

#------------------------------------------------------------------------------

class ConfigurationError(Exception):
    pass

#------------------------------------------------------------------------------

class FactsheetFolder(Folder):
    def __init__(self, id, title, administrator_email,
                    introduction = 'Introduction text',
                    instructions = 'Instructions text',
                    sender_email = 'no-reply@eea.europa.eu',
                    smtp = 'localhost',
                    smtp_port = '25'):
        """ constructor """
        self.id = id
        self.title = title
        self.administrator_email = administrator_email
        self.introduction =introduction
        self.instructions = instructions
        self.sender_email = sender_email
        self.smtp = smtp
        self.smtp_port = smtp_port

    meta_type = "OMI Factsheet Folder"
    security = ClassSecurityInfo()

    index_html = PageTemplateFile('zpt/folder_index', globals())
    instructions_html = PageTemplateFile('zpt/folder_instructions', globals())
    base_html = PageTemplateFile('zpt/base_template', globals())
    _search_html = PageTemplateFile('zpt/search', globals())
    _edit_html = PageTemplateFile('zpt/folder_edit', globals())
    manage_addFactsheet_html = manage_addFactsheet_html

    security.declareProtected(MANAGE_FACTSHEET_FOLDER, 'edit_html')
    def edit_html(self, REQUEST):
        """ edit folder properties - for the moment just the administrator email"""
        submit = REQUEST.get('save', '')
        if submit:
            self.title = REQUEST.form.get('title')
            self.administrator_email = REQUEST.form.get('administrator_email')
            self.introduction = REQUEST.form.get('introduction')
            self.instructions = REQUEST.form.get('instructions')
            self.sender_email = REQUEST.form.get('sender_email')
            self.smtp = REQUEST.form.get('smtp')
            self.smtp_port = REQUEST.form.get('smtp_port')
            self.folder_add_edit_notification(self.administrator_email)
            REQUEST.RESPONSE.redirect('index_html')
        return self._edit_html(REQUEST)

    security.declareProtected(view, 'add_html')
    def add_html(self):
        """ """
        return self.manage_addFactsheet_html(self.REQUEST)

    def getFactsheetFolder(self):
        """ return self """
        return self

    def search_html(self, REQUEST=None):
        """ advanced search """
        results = []
        submit = REQUEST.get('search_models', '')
        mode = REQUEST.get('mode', '')
        if submit:
            catalogue = self.catalogue
            query = REQUEST.form.get('query', '')
            filters = {}
            if query:
                filters['model_keywords'] = query.translate(string.maketrans('*:\'"()[]{}', '__________'))
            if mode:
                # advanced search
                for k,v in REQUEST.form.items():
                    if k in searchable_lists:
                        filters[k] = v
            if filters:
                results = catalogue(filters)
                results = list(set(results))    # get brains
                results = list(get_objects(catalogue, results))   # get the actual objects
        return self._search_html(REQUEST, themes_covered = potential_themes, dominant_analytical_techniques = analytical_techniques, results=results)

    def add_message(self, message):
        self.REQUEST.SESSION.set('message', message)

    def show_message(self):
        message = self.REQUEST.SESSION.get('message', '')
        if message:
            self.REQUEST.SESSION.set('message', '')
        return message

    security.declareProtected(MANAGE_FACTSHEET, 'deleteFactsheet')
    def deleteFactsheet(self, REQUEST):
        """ Remove a factsheet"""
        id=REQUEST.form.get('factsheet_id')
        self.manage_delObjects(id)
        self.add_message('Model successfully deleted!')
        REQUEST.RESPONSE.redirect('index_html')

#    security.declarePrivate('get_mailhost')
#    def get_mailhost(self):
#        """ """
#        try:
#            ob = getattr(self, MAILHOST, None)
#            if isinstance(ob, MailHost):
#                return ob
#        except:
#            pass
#        raise ConfigurationError('Expected a MailHost object named '
#            '"MailHost". Please create one.')

    security.declarePrivate('send_mail')
    def send_mail(self, msg_to, msg_subject, msg_body, msg_body_text):
#        mailhost = self.get_mailhost()
#
#        from email.MIMEText import MIMEText
#        from email.MIMEMessage import MIMEMessage
#
#        msg = MIMEMessage(MIMEText(msg_body.encode('utf-8'), _charset='utf-8'))
#        msg['Subject'] = msg_subject
#        msg['From'] = self.administrator_email
#        msg['To'] = msg_to
#
#        mailhost.send(msg.as_string())
        import smtplib

        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = msg_subject
        msg['From'] = self.sender_email
        msg['To'] = msg_to

        # Create the body of the message (a plain-text and an HTML version).
        text = msg_body_text
        html = msg_body

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)

        # Send the message via local SMTP server.
        s = smtplib.SMTP(self.smtp, self.smtp_port)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(self.sender_email, msg_to, msg.as_string())
        s.quit()

    security.declarePrivate('getCatalogedObjects')
    def getCatalogedObjects(self, meta_type=None, approved=0, howmany=-1, sort_on='releasedate', sort_order='reverse', has_local_role=0, **kwargs):
        results = []
        filter = {'submitted': 1} # only submitted items
        if approved == 1: l_filter['approved'] = 1
        if has_local_role == 1: filter['has_local_role'] = 1
        if sort_on != '':
            filter['sort_on'] = sort_on
            if sort_order != '':
                filter['sort_order'] = sort_order
        if meta_type: filter['meta_type'] = self.utConvertToList(meta_type)
        else: filter['meta_type'] = self.searchable_content
        # extra filters
        filter.update(kwargs)
        # perform the search
        results = self.__searchCatalog(filter)
        if howmany != -1:
            results = results[:howmany]
        results = self.__getObjects(results)
        return results

    security.declarePrivate('folder_add_edit_notification')
    def folder_add_edit_notification(self, email):
        """ send a notification when a folder is added / edited / commented"""
#        mailhost = self.get_mailhost()
#        if mailhost:
        values = {'folder_view_link': '%s' % self.absolute_url()}
        self.send_mail(msg_to=email,
                        msg_subject='%s - Folder added / edited' % self.title,
                        msg_body=FOLDER_ADD_EDIT_TEMPLATE % values,
                        msg_body_text=FOLDER_ADD_EDIT_TEMPLATE_TEXT % values
                        )

    def generate_password(self, email, passwordLength = 8):
        from random import Random

        # if the email is found in another model, the same password will be set
        for model in self.objectValues('OMI Factsheet'):
            if model.contact_email == email:
                return model.password

        rnd = Random()
        righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
        lefthand = '789yuiophjknmYUIPHJKLNM'
        password = ''
        for i in range(passwordLength):
            if i%2:
                password += rnd.choice(lefthand)
            else:
                password += rnd.choice(righthand)
        return password

    def newlineToBr(self, text):
        """ """
        if text.find('\r') >= 0: text = ''.join(text.split('\r'))
        if text.find('\n') >= 0: text = '<br />'.join(text.split('\n'))
        return text

    def formatDateTime(self, date):
        """date is a DateTime object. This function returns a string 'dd month_name yyyy hh:mm:ss'"""
        try: return date.strftime('%d %B %Y %H:%M')
        except: return ''

    security.declarePublic('canManageFactsheetFolder')
    def canManageFactsheetFolder(self):
        """ Check the permissions to edit/delete factsheets """
        return checkPermission(MANAGE_FACTSHEET_FOLDER, self)

    security.declarePublic('get_models')
    def get_models(self):
        """ return the factsheet objects from the folder """
        return self.objectValues('OMI Factsheet')

InitializeClass(FactsheetFolder)

