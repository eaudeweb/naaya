
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *

manage_addEmailTemplateForm = PageTemplateFile('zpt/emailtemplate_add', globals())
def manage_addEmailTemplate(self, id='', title='', body='', REQUEST=None):
    """ """
    ob = EmailTemplate(id, title, body)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class EmailTemplate(SimpleItem):
    """ """

    meta_type = METATYPE_EMAILTEMPLATE
    icon = 'misc_/NaayaCore/EmailTemplate.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, body):
        """ """
        self.id = id
        self.title = title
        self.body = body

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', body='', REQUEST=None):
        """ Update settings """
        self.title = title
        self.body = body
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/emailtemplate_properties', globals())

InitializeClass(EmailTemplate)
