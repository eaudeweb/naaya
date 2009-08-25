from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

add_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_registration(self, id='', title='', REQUEST=None):
    """ Adds a Semide registration instance"""
    ob = SemideRegistration(id, title)
    self._setObject(id, ob)
    if REQUEST:
        REQUEST.RESPONSE.redirect(self.absolute_url())

class SemideRegistration(Folder):
    """ Main class of the meeting registration"""

    meta_type = 'Semide Registration'
    product_name = 'SemideRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id = id
        self.title = title

    registration = PageTemplateFile('zpt/registration/registration', globals())
    registration_press = PageTemplateFile('zpt/registration/registration_press', globals())


InitializeClass(SemideRegistration)