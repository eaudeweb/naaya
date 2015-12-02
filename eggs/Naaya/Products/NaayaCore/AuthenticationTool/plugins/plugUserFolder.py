from zope.interface import implements
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.AuthenticationTool.plugBase import PlugBase
from Products.NaayaCore.AuthenticationTool.interfaces import \
                                            IAuthenticationToolPlugin

class plugUserFolder(PlugBase):
    """ Plugin for User Folder """

    implements(IAuthenticationToolPlugin)

    object_type = 'User Folder'
    meta_type = 'Plugin for user folder'

    security = ClassSecurityInfo()

    security.declarePublic('interface_html')
    interface_html = PageTemplateFile('plugUserFolder', globals())

    def getUserFullName(self, user_id, acl_folder):
        return user_id

InitializeClass(plugUserFolder)
