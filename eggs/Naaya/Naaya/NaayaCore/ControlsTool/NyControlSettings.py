#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *


def manage_addNyControlSettings(self, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """

    id = ID_CONTROLSTOOL
    title = TITLE_CONTROLSTOOL
    ob = NyControlSettings(id, title, settings={})
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class NyControlSettings(Folder):

    meta_type = 'Naaya Control Settings'
    icon = 'misc_/NaayaCore/ControlsTool.gif'

    manage_options = (
        Folder.manage_options[0:1]
        +
        (
            {'label': 'Properties', 'action': 'manage_control_generic'},
        )
        +
        Folder.manage_options[3:8]
    )

    all_meta_types = ()

    security = ClassSecurityInfo()

    def __init__(self, id, title, settings):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        self.settings={}

    def saveSettings(self, enabled_for=[], REQUEST=None):
        """ """
        #TODO: to save as values (image src, label)
        self.settings = {}
        for k in enabled_for:
            self.settings[k] = True
        self._p_changed = 1

    def checkControl(self, meta_type=''):
        """ """
        if meta_type == 'Naaya GeoPoint': return False
        if self.settings.has_key(meta_type):
            return self.settings[meta_type]
        else:
            return False

    def getMapControlProps(self):
        """ """
        #TODO: this list should be dynamic and defined via ZMI
        return ['longitude', 'latitude', 'address', 'url', 'geo_type']

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_control_generic')
    manage_control_generic = PageTemplateFile('zpt/manage_control_generic', globals())

InitializeClass(NyControlSettings)