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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Alex Morega, Eau de Web

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime

# Naaya imports
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES, \
                                         PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.managers.utils import genObjectId, genRandomId
from Products.NaayaCore.managers.utils import utils
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty

from geo import Geo

WIDGET_ID_SUFFIX = '-property'

DATA_TYPES = {
    'int': int,
    'str': unicode,
    'float': float,
    'bool': bool,
    'date': DateTime,
    'geo': Geo,
}


def propname_from_widgetid(widgetid):
    if not widgetid.endswith(WIDGET_ID_SUFFIX):
        raise ValueError('Widget ID does not end with '
            'WIDGET_ID_SUFFIX ("%s")' % WIDGET_ID_SUFFIX)
    return widgetid[:-len(WIDGET_ID_SUFFIX)]

def widgetid_from_propname(propname):
    """ construct a widget's id based on the property's name """
    # we avoid using "_" as a separator because Localizer will
    # recognise it as a separator and throw manage_addWidget in
    # an endless loop
    return propname + WIDGET_ID_SUFFIX


class WidgetError(Exception):
    """Widget error"""
    pass

def manage_addWidget(klass, container, id="", title=None, REQUEST=None, **kwargs):
    """Add widget"""
    if not title:
        title = str(klass)
    if not id:
        # prevent any name clashes by using the 'w_' prefix
        id = 'w_' + genObjectId(title)

    idSuffix = ''
    while (id+idSuffix in container.objectIds() or
           getattr(container, id+idSuffix, None) is not None):
        idSuffix = genRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = None
    if REQUEST is not None:
        lang = REQUEST.form.get('lang', None)
    if not lang:
        lang = kwargs.get('lang', container.gl_get_selected_language())
    widget = klass(id, title=title, lang=lang, **kwargs)

    container.gl_add_languages(widget)
    container._setObject(id, widget)
    widget = container._getOb(id)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
    return id

class Widget(Folder, LocalPropertyManager):
    """ Abstract class for widget
    """
    meta_type = 'Naaya Schema Widget'
    meta_sortorder = 100 # used to sort the list of available widget types

    security = ClassSecurityInfo()

    # Subobjects
    all_meta_types = ()

    # ZMI Tabs
    manage_options=(
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','ObjectManager_Contents.stx')},
        )

    # Properties
    _properties=(
        {'id':'sortorder', 'type': 'int', 'mode':'w', 'label': 'Sort order'},
        {'id':'required', 'type': 'boolean', 'mode':'w', 'label': 'Required widget'},
        {'id':'default','mode':'w', 'label': 'Default value'},
        {'id':'localized', 'mode':'w', 'type': 'boolean'},
        {'id':'data_type', 'mode':'w', 'type': 'string'},
        {'id':'visible', 'mode':'w', 'type': 'boolean'},
    )

    multiple_form_values = False

    sortorder = 100
    required = False
    default = None
    localized = False
    data_type = 'str'
    visible = True

    # Local properties
    title = LocalProperty('title')

    def __init__(self, id, title='', lang=None):
        Folder.__init__(self, id=id)
        self.set_localproperty('title', 'string', lang)
        self._setLocalPropValue('title', lang, title)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ Update widget properties"""
        if REQUEST:
            kwargs.update(REQUEST.form)

        _lang = kwargs.get('lang', self.get_selected_language())
        _required = bool(kwargs.get('required'))

        if not _required and self.must_be_mandatory():
            raise ValueError('Can not make property "%s" non-mandatory'
                % self.prop_name())

        self._setLocalPropValue('title', _lang, kwargs.get('title'))
        self.required = _required
        self.sortorder = int(kwargs.get('sortorder'))
        self.visible = bool(kwargs.get('visible'))

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    def must_be_mandatory(self):
        return (self.get_default_definition() or {}).get('required', False)

    security.declarePrivate('get_default_definition')
    def get_default_definition(self):
        default_definition = self.getParentNode().getDefaultDefinition()
        if default_definition is not None:
            return default_definition.get(self.prop_name(), None)
        return None

    #
    # To be implemented or ovewritten (if needed) by widget concrete classes.
    #
    def isEmptyDatamodel(self, value):
        return value is None

    def parseFormData(self, data):
        return data

    def validateDatamodel(self, value):
        """Validate datamodel"""
        if self.required and self.isEmptyDatamodel(value):
            raise WidgetError('Value required for "%s"' % self.title)

    security.declarePrivate('getPropertyType')
    def getDataType(self):
        return DATA_TYPES[self.data_type]

    security.declarePrivate('convertValue')
    def convertValue(self, value):
        convert = DATA_TYPES[self.data_type]
        try:
            if value == '':
                # special cases for empty values
                if convert in (int, float):
                    value = 0
                elif convert is DateTime:
                    value = None
            return convert(value)
        except ValueError:
            raise WidgetError('Conversion error: expected %s value '
                'for "%s"' % (self.data_type, self.prop_name()))

    def prop_name(self):
        return propname_from_widgetid(self.getId())

    def index_html(self, REQUEST):
        """ redirect to admin_html """
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    def _convert_to_form_string(self, value):
        """ by default this does nothing; subclasses may override. """
        return value

    def render_html(self, value, errors=None):
        value = self._convert_to_form_string(value)
        if self.visible:
            return self.template(value=value, errors=errors)
        else:
            return self.hidden_template(value=value)

    def get_widget_type(self):
        classname = self.__class__.__name__
        if classname.endswith('Widget') and len(classname) > len('Widget'):
            return classname[:-len('Widget')]
        else:
            raise ValueError('Bad Widget class name: %s' % classname)

    def convert_from_user_string(self, value):
        """ Convert a user-readable string to a value that can be saved """
        return value

    def convert_to_user_string(self, value):
        """ Convert a database value to a user-readable string """
        return value

    hidden_template = PageTemplateFile('../zpt/property_widget_hidden', globals())

    admin_html = PageTemplateFile('../zpt/admin_schema_property', globals())

InitializeClass(Widget)
