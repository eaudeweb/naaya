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
        Folder.manage_options[1:1]
        +
        (
            {'label': 'Properties', 'action': 'manage_control_generic'},
        )
        +
        Folder.manage_options[5:6]
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

    def saveSettings(self, enabled_for=[], add_props=False, REQUEST=None):
        """ """
        if add_props: add_props = True

        old_settings = self.settings.keys()
        new_settings = enabled_for

        to_remove = []
        to_add = []

        for s in old_settings:
            if s not in new_settings:
                to_remove.append(s)

        for s in new_settings:
            if s not in old_settings:
                to_add.append(s)
            elif not self.hasAdditionalProperties(s) and add_props:
                self.add_additionalProperties(s)

        for s in to_remove:
            del self.settings[s]
            if add_props:
                self.del_additionalProperties(s)

        for s in to_add:
            self.settings[s] = True
            if add_props:
                self.add_additionalProperties(s)
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

    def del_additionalProperties(self, name):
        props = ['landscape_type', 'administrative_level']
        dp_tool = self.getDynamicPropertiesTool()
        if hasattr(dp_tool, name):
            dp_item = dp_tool._getOb(name)
            try:
                dp_item.manageDeleteDynamicProperties(props)
            except KeyError:
                pass

    def add_additionalProperties(self, name):
        properties = [('landscape_type', 'Landscape type', 'Unspecified', '0'), 
                      ('administrative_level', 'Administrative level', 'National', '10')]
        dp_tool = self.getDynamicPropertiesTool()
        ct_tool = self.getCatalogTool()

        if not hasattr(dp_tool, name):
            dp_tool.manage_addDynamicPropertiesItem(id=name)
        dp_item = dp_tool._getOb(name)
        for k, v, x, z in properties:
            dp_item.manageAddDynamicProperty(id=k,
                                             name=v,
                                             searchable='1',
                                             type='selection',
                                             defaultvalue=x,
                                             values='',
                                             ref_list=k,
                                             order=z
                                             )
            try:
                ct_tool.addIndex(k, 'FieldIndex', k)
            except:
                pass
            try:
                ct_tool.manage_reindexIndex(k)
            except:
                pass

    def hasAdditionalProperties(self, name):
        dp_tool = self.getDynamicPropertiesTool()
        return name in dp_tool.getDynamicProperties(name)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_control_generic')
    manage_control_generic = PageTemplateFile('zpt/manage_control_generic', globals())

InitializeClass(NyControlSettings)