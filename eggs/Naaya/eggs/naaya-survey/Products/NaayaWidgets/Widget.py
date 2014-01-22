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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES, \
                                         PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.managers.utils import slugify, genRandomId
from Products.NaayaCore.managers.utils import utils
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty

class WidgetError(Exception):
    """Widget error"""
    pass

def manage_addWidget(klass, container, id="", title=None, REQUEST=None, **kwargs):
    """Add widget"""
    if not title:
        title = str(klass)
    if not id:
        # prevent any name clashes by using the 'w_' prefix
        id = 'w_' + slugify(title)

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
    meta_type = 'Naaya Widget'
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
        {'id':'sortorder', 'type': 'int','mode':'w', 'label': 'Sort order'},
        {'id':'required', 'type': 'boolean','mode':'w', 'label': 'Required widget'},
    )

    sortorder = 100
    required = False
    localized = False

    # Local properties
    title = LocalProperty('title')
    tooltips = LocalProperty('tooltips')

    common_render_meth = PageTemplateFile('widgets/zpt/widget_common', globals())

    def __init__(self, id, lang=None, **kwargs):
        Folder.__init__(self, id=id)
        self.set_localproperty('title', 'string', lang)
        self.set_localproperty('tooltips', 'text', lang)
        self.saveProperties(lang=lang, **kwargs)

    security.declarePublic('getWidgetId')
    def getWidgetId(self):
        """ Returns widget id"""
        return self.getId()

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ Update widget properties"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        local_properties = self.getLocalProperties()
        local_properties = filter(None,
                                  [x.get('id', None) for x in local_properties]
                              )
        # Update local properties
        lang = kwargs.get('lang', self.get_selected_language())
        for local_property in local_properties:
            if not kwargs.has_key(local_property):
                continue
            prop_value = kwargs.get(local_property, '')

            # Strip empty values:
            if type(prop_value) in (str, unicode):
                prop_value = prop_value.strip()
            # Filter/strip empty values
            if type(prop_value) in (list, tuple):
                prop_value = [x.strip() for x in prop_value if x.strip()]
            if type(prop_value) == tuple:
                prop_value = tuple(prop_value)
            self.set_localpropvalue(local_property, lang, prop_value)
        # Update non local properties
        kwargs = dict([(key, value) for key, value in kwargs.items()
                       if key not in local_properties])
        self.manage_changeProperties(**kwargs)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    def _get_default_value(self, **kwargs):
        return '-'
    #
    # To be implemented or ovewritten (if needed) by widget concrete classes.
    #
    def isEmptyDatamodel(self, value):
        return value is None

    def validateDatamodel(self, value):
        """Validate datamodel"""
        if self.required and self.isEmptyDatamodel(value):
            raise WidgetError('Value required for "%s"' % self.title)

    def prepare(self, datamodel, **kwargs):
        """ Prepare value to be stored according with widget type"""
        pass

    security.declareProtected(view, 'render')
    def render(self, mode, datamodel=None, **kwargs):
        """Render widget according with given mode"""
        assert(mode in ('view', 'edit', 'manage'))
        return self.render_meth(mode=mode, datamodel=datamodel, **kwargs)

    security.declareProtected(view, 'get_value')
    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if datamodel is None:
            return ''
        if isinstance(datamodel, dict):
            lang = self.gl_get_selected_language()
            return datamodel[lang]
        return datamodel

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit')
    edit = PageTemplateFile('zpt/edit_widget', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self):
        """ """
        local_properties = self.getLocalProperties()
        local_properties = filter(None,
                                  [x.get('id', None) for x in local_properties]
                              )
        lang = self.get_selected_language()
        other_languages = [language for language in self.gl_get_languages()
            if language != lang]
        if 'choices' in local_properties:
            choices = self.getLocalAttribute('choices', lang)
            for language in other_languages:
                other_choices = len(self.getLocalAttribute('choices', language))
                if (len(choices) != other_choices and other_choices):
                    errors = self.getSessionErrors() or []
                    errors.append('This question has a different '
                        'number of choices (%s) in %s. Reports cannot be generated '
                        'until this is corrected.'
                        % (other_choices, self.gl_get_language_name(language)))
                    self.setSessionErrorsTrans(errors)
        return self.edit()

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'preview_html')
    preview_html = PageTemplateFile('zpt/preview_widget', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'index_html')
    index_html = preview_html

    def getNonEmptyAttribute(self, attrName):
        """ Return the value of the first non empty <attrName> local atribute."""
        return self.getLocalAttribute(attrName, langFallback=True)

InitializeClass(Widget)
