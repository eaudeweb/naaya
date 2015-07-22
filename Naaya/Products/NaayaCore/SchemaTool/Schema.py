from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.constants import *
from naaya.core.zope2util import folder_manage_main_plus

from widgets.Widget import WidgetError, DATA_TYPES, widgetid_from_propname

known_widget_types = [
    'String', 'TextArea', 'Date', 'Interval', 'Checkbox', 'URL',
    'Select', 'SelectMultiple', 'Glossary', 'Geo', 'GeoType', 'Pointer', 'File',
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

    meta_types = tuple( {
            'name': meta_type,
            'action': widget_constructors[
                            widget_types_by_metatype[meta_type]].func_name,
            'permission': view_management_screens,
        } for meta_type in widget_types_by_metatype)

    all_meta_types = meta_types

    is_ratable = False

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

        # manually set the keywords & coverage glossaries (ugly hack)
        def set_glossary(name):
            prop_name = '%s-property' % name
            if prop_name not in self.objectIds(['Naaya Schema Glossary Widget']):
                return
            value = getattr(self.getSite(), '%s_glossary' % name, None)
            if value is None:
                return
            self[prop_name].glossary_id = value
        set_glossary('keywords')
        set_glossary('coverage')

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

        for name, value in kwargs.iteritems():
            if name == 'data_type' and value not in DATA_TYPES:
                raise ValueError('Unknown data format "%s"' % value)
            elif name == 'default':
                widget.default = value
            elif name == 'translation_id':
                widget.translation_id = value
                widget._p_changed = True
            else:
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

            value = widget.convert_formvalue_to_pythonvalue(raw_value)

            if value is None:
                if not _all_values:
                    continue
                if widget.data_type == 'list':
                    value = []
                else:
                    value = widget.default

            errors = []
            try:
                widget.validateDatamodel(value)
                # we pass a doctored dict that looks like what our widget expects from the form
                widget_value = widget.parseFormData(value)
                form_data[field_name] = widget.convertValue(widget_value)
            except WidgetError, e:
                errors.append(str(e))
                form_data[field_name] = value

            if errors:
                form_errors[field_name] = errors

        return form_data, form_errors

    security.declarePrivate('get_content_type')
    def get_content_type(self):
        """ Get content_type with this schema attached"""
        for content_type in self.get_pluggable_content().values():
            if self.id == content_type.get('schema_name', None):
                return content_type
        return None

    security.declarePrivate('getDefaultDefinition')
    def getDefaultDefinition(self):
        """ get initial definition for this schema, from the NyZzz Python module """
        content_type = self.get_content_type()
        if content_type is not None:
            return content_type.get('default_schema', None)
        else:
            return None

    def index_html(self, REQUEST):
        """ redirect to admin_html """
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_html')
    admin_html = PageTemplateFile('zpt/admin_schema', globals())

    manage_main = folder_manage_main_plus
    _manage_extra_footer = PageTemplateFile('zpt/manage_extra_footer', globals())
    security.declareProtected(view_management_screens, 'ny_after_listing')
    def ny_after_listing(self):
        options = {
            'widget_types': widget_constructors.keys(),
            'data_types': DATA_TYPES,
        }
        return self._manage_extra_footer(**options)

InitializeClass(Schema)
