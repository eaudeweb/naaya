
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.AuthenticationTool.plugBase import PlugBase

plug_name = 'plugUserFolder'
plug_doc = 'Plugin for User Folder'
plug_version = '1.0.0'
plug_object_type = 'User Folder'

class plugUserFolder(PlugBase):
    """ """

    meta_type = 'Plugin for user folder'

    def __init__(self):
        """ constructor """
        PlugBase.__dict__['__init__'](self)

    security = ClassSecurityInfo()

    security.declarePublic('interface_html')
    interface_html = PageTemplateFile('plugUserFolder', globals())

    def getUserFullName(self, user_id, acl_folder):
        return user_id

InitializeClass(plugUserFolder)
