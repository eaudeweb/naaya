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
# Alex Morega, Eau de Web

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.constants import *
from widgets.Widget import WidgetError, DATA_TYPES, widgetid_from_propname

known_widget_types = [
    'String', 'TextArea', 'Date', 'Checkbox',
    'Select', 'Glossary', 'Geo', 'GeoType', 'Pointer',
]

# widgets
def _load_widgets():
    widget_constructors = {}
    widget_types_by_metatype = {}
    for name in known_widget_types:
        module_name = 'widgets.%sWidget' % name
        method_name = 'add%sWidget' % name
        class_name = '%sWidget' % name
        i = __import__(module_name, globals(), locals(), [method_name, class_name])
        meta_type = getattr(i, class_name).meta_type
        widget_constructors[name] = getattr(i, method_name)
        widget_types_by_metatype[meta_type] = name
    return widget_constructors, widget_types_by_metatype

widget_constructors, widget_types_by_metatype = _load_widgets()

class Schema(Folder):
    """ Container for Schema objects """

    meta_type = METATYPE_SCHEMA
#     _icon = '_misc/NaayaCore/Schema.gif'

    security = ClassSecurityInfo()

    meta_types = ()
    all_meta_types = meta_types

    def __init__(self, id, title):
        super(Schema, self).__init__(id=id)
        self.title = title

    security.declareProtected(view_management_screens, 'manage_addWidget_html')
    manage_addWidget_html = PageTemplateFile('zpt/propdef_add', globals())

    security.declareProtected(view_management_screens, 'manage_addWidget')
    def manage_addWidget(self, name, widget, REQUEST):
        """ form submit handler to create new property definition """
        self.addWidget(name, widget)
        return self.manage_main(self, REQUEST, update_menu=1)

    def saveProperties(self, title='', REQUEST=None):
        """ Save properties for this Schema """
        self.title = title
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declarePrivate('populateSchema')
    def populateSchema(self, schema_def):
        """
        Populate this schema with properties from schema_def - this
        is typically called when creating a new SchemaTool
        instance (which happens when creating a new NySite). If the
        Schema instance already contains any
        properties, this method raises ValueError.
        """

        if self.objectIds():
            raise ValueError('Schema "%s" has already been populated' % self.title_or_id())
        for name, data in schema_def.iteritems():
            self.addWidget(name, **data)

    security.declareProtected(view_management_screens, 'manage_addProperty')
    def manage_addProperty(self, REQUEST):
        """ Web method to create property widgets from ZMI """
        self.addWidget(**REQUEST.form)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_workspace')

    security.declarePrivate('addWidget')
    def addWidget(self, name, **kwargs):
        """ Add a Widget object to this schema """

        propdef_id = widgetid_from_propname(name)
        title = kwargs.get('label', name)

        widget_id = widget_constructors[kwargs['widget_type']](self, id=propdef_id, title=title)
        widget = self._getOb(widget_id)

        # TODO: if there are other names in kwargs, raise a KeyError
        for name in ['sortorder', 'required', 'localized',
                'tinymce', 'data_type', 'visible', 'glossary_id',
                'list_id', 'default']:
            if name in kwargs:
                value = kwargs[name]
                if name == 'data_type' and value not in DATA_TYPES:
                    raise ValueError('Unknown data format "%s"' % value)
                widget.manage_changeProperties(**{name: value})

        return widget

    def getWidget(self, prop_name):
        """ Look up and return a property in this schema """
        try:
            return self._getOb(widgetid_from_propname(prop_name))
        except AttributeError:
            raise KeyError('Property "%s" not found in schema "%s"' \
                    % (prop_name, self.title_or_id()))

    def listWidgets(self):
        """ List this schema's properties, sorted by their sortorder """
        output = list(self.objectValues())
        output.sort(key=lambda widget: widget.sortorder)
        return output

    security.declarePrivate('listPropNames')
    def listPropNames(self, local=False):
        """
        Returns a set with the names of all properties (or just the localized
        ones) defined in this Schema.
        """
        widgets = self.objectValues()
        if local:
            widgets = filter(lambda w: w.localized, widgets)
        return set(map(lambda w: w.prop_name(), widgets))

    security.declarePrivate('processForm')
    def processForm(self, form, _all_values=True):
        """
        Parse the given form against this schema, do validation, then
        return the data and any errors
        """

        form_data = {}
        form_errors = {}

        for widget in self.objectValues():
            field_name = widget.prop_name()

            if field_name in form:
                raw_value = form[field_name]
            elif widget.multiple_form_values:
                raw_value = {}
                for key, value in form.iteritems():
                    if key.startswith(field_name + '.'):
                        raw_value[key[len(field_name)+1:]] = value
                if not raw_value:
                    raw_value = None
            else:
                raw_value = None

            if raw_value is None:
                if not _all_values:
                    continue

                if widget.default is not None:
                    raw_value = widget.default
                else:
                    raw_value = ''

            errors = []
            try:
                widget.validateDatamodel(raw_value)
                # we pass a doctored dict that looks like what our widget expects from the form
                widget_value = widget.parseFormData(raw_value)
                form_data[field_name] = widget.convertValue(widget_value)
            except WidgetError, e:
                errors.append(str(e))
                form_data[field_name] = raw_value

            if errors:
                form_errors[field_name] = errors

        return form_data, form_errors

    security.declarePrivate('getDefaultDefinition')
    def getDefaultDefinition(self):
        """ get initial definition for this schema, from the NyZzz Python module """
        for content_type in self.get_pluggable_content().values():
            if self.id == content_type['module']:
                return content_type['default_schema']
        return None

    def index_html(self, REQUEST):
        """ redirect to admin_html """
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_html')
    admin_html = PageTemplateFile('zpt/admin_schema', globals())

    _manage_extra_footer = PageTemplateFile('zpt/manage_extra_footer', globals())

    def manage_page_footer(self):
        kwargs = {
            'widget_types': widget_constructors.keys(),
            'data_types': DATA_TYPES,
        }
        our_footer = self._manage_extra_footer(**kwargs)
        orig_footer = super(Schema, self).manage_page_footer()
        return our_footer + orig_footer

InitializeClass(Schema)
