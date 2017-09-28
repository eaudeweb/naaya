
from zope.interface import implements
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

from Products.NaayaCore.interfaces import IDynamicPropertiesItem
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from managers.dynamic_properties_tool import dynamic_properties_tool

manage_addDynamicPropertiesItemForm = PageTemplateFile('zpt/dynamicpropertiesitem_add', globals())
def manage_addDynamicPropertiesItem(self, id='', title='', REQUEST=None):
    """ """
    ob = DynamicPropertiesItem(id, title)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class DynamicPropertiesItem(SimpleItem, utils, dynamic_properties_tool):
    """ DynamicPropertiesItem class """

    implements(IDynamicPropertiesItem)

    meta_type = METATYPE_DYNAMICPROPERTIESITEM
    icon = 'misc_/NaayaCore/DynamicPropertiesItem.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'Settings', 'action': 'manage_settings_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        utils.__dict__['__init__'](self)
        dynamic_properties_tool.__dict__['__init__'](self)

    security.declareProtected(view_management_screens, 'manageSettings')
    def manageSettings(self, title='', REQUEST=None):
        """ """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_settings_html')

    security.declareProtected(view_management_screens, 'manageAddDynamicProperty')
    def manageAddDynamicProperty(self, id='', searchable='', name='', type='',
        required='', defaultvalue='', values='', order='', ref_list='', REQUEST=None):
        """ """
        lang = self.gl_get_selected_language()
        if searchable: searchable=1
        else: searchable=0
        if required: required=1
        else: required=0
        try: order = abs(int(order))
        except: order = 0
        if ref_list:
            values = {}
            ref_items = self.get_list_nodes(ref_list)
            values[ref_list] = self.utConvertListToLines([x.title for x in ref_items])
        self.addDynamicProperty(id, searchable, name, type, required, defaultvalue, values, order)
        #create objects dynamic properties
        for l_object in self.getCatalogedObjects(self.id):
            l_object.createProperty(id, defaultvalue, lang)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    security.declareProtected(view_management_screens, 'manageUpdateDynamicProperty')
    def manageUpdateDynamicProperty(self, id='', searchable='', name='', type='',
        required='', defaultvalue='', values='', order='', ref_list='', REQUEST=None):
        """ """
        lang = self.gl_get_selected_language()
        if searchable: searchable=1
        else: searchable=0
        if required: required=1
        else: required=0
        try: order = abs(int(order))
        except: order = 0
        if ref_list:
            values = {}
            ref_items = self.get_list_nodes(ref_list)
            values[ref_list] = self.utConvertListToLines([x.title for x in ref_items])
        self.updateDynamicProperty(id, searchable, name, type, required, defaultvalue, values, order)
        #update objects dynamic properties
        for l_object in self.getCatalogedObjects(self.id):
            previousvalue = l_object.getPropertyValue(id, lang)
            l_object.createProperty(id, previousvalue, lang)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    security.declareProtected(view_management_screens, 'manageDeleteDynamicProperties')
    def manageDeleteDynamicProperties(self, id=[], REQUEST=None):
        """ """
        l_ids = self.utConvertToList(id)
        self.deleteDynamicProperty(l_ids)
        #delete objects dynamic properties
        for l_object in self.getCatalogedObjects(self.id):
            map(l_object.deleteProperty, l_ids)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    #ZMI forms
    security.declareProtected(view_management_screens, 'manage_settings_html')
    manage_settings_html = PageTemplateFile('zpt/dynamicpropertiesitem_settings', globals())

    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/dynamicpropertiesitem_properties', globals())

InitializeClass(DynamicPropertiesItem)
