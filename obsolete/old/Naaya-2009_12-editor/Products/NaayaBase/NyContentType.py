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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
# Alex Morega, Eau de Web


from copy import deepcopy

from AccessControl import ClassSecurityInfo, SpecialUsers
from AccessControl.Permissions import view
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements

from Products.Localizer.LocalPropertyManager import LocalPropertyManager
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaCore.constants import ID_SCHEMATOOL
from naaya.content.base.interfaces import INyContentObject

NY_CONTENT_BASE_SCHEMA = {
    'title':        dict(sortorder=10, widget_type='String', label='Title', required=True, localized=True),
    'description':  dict(sortorder=20, widget_type='TextArea', label='Description', localized=True, tinymce=True),
    'geo_location': dict(sortorder=24, widget_type='Geo', data_type='geo', label='Geographical location', visible=False),
    'geo_type':     dict(sortorder=26, widget_type='GeoType', data_type='str', label='Geographical location type', visible=False),
    'coverage':     dict(sortorder=30, widget_type='Glossary', label='Geographical coverage', glossary_id='coverage', localized=True),
    'keywords':     dict(sortorder=40, widget_type='Glossary', label='Keywords', glossary_id='keywords', localized=True),
    'sortorder':    dict(sortorder=50, widget_type='String', data_type='int', default='100', label='Sort order', required=True),
    'releasedate':  dict(sortorder=60, widget_type='Date', data_type='date', label='Release date', required=True),
    'discussion':   dict(sortorder=70, widget_type='Checkbox', data_type='int', label='Open for comments'),
}

class SchemaFormHelper(object):
    """
    Helper object for rendering forms: lists widgets, fills in values, and
    displays form errors
    """
    def __init__(self, schema, context, value_callback=None):
        self.schema = schema
        self.context = context
        self.value_callback = value_callback

    def form_items(self):
        def get_value(prop_name):
            if self.value_callback:
                value = self.value_callback(prop_name)
                if value is not None:
                    return value
            widget = self.schema.getWidget(prop_name)
            prop_type = widget.getDataType()
            val = self.context.getSession(prop_name, '')
            if val == '':
                if widget.default is not None:
                    return prop_type(widget.default)
                else:
                    return prop_type()
            else:
                return prop_type(val)

        def get_renderer(prop_name, widget):
            value = get_value(prop_name)
            errors = self.context.getSession('%s-errors' % prop_name, None)
            return lambda: widget.render_html(value=value, errors=errors)

        for widget in self.schema.listWidgets():
            prop_name = widget.prop_name()
            yield {'name': prop_name, 'html': get_renderer(prop_name, widget)}

    def del_schema_session_values(self):
        for key in self.schema.listPropNames():
            self.context.delSession(key)
        for key in self.context.REQUEST.SESSION.keys():
            # We remove anything that ends in '-errors', not just schema
            # errors. This is not ideal, but content types sometimes expect
            # their own non-schema errors to be removed by us.
            if key.endswith('-errors'):
                self.context.delSession(key)

    def get_meta_label(self):
        return self.schema.title_or_id()


def get_schema_helper_for_metatype(context, meta_type, value_callback=None):
    schema = context.getSite()._getOb(ID_SCHEMATOOL).getSchemaForMetatype(meta_type)
    return SchemaFormHelper(schema, context, value_callback)


class NyContentType:
    """
    Base class for NyZzz classes - wrapper for NyContentData instances
    that handle editing, displaying, etc.
    """

    implements(INyContentObject)

    security = ClassSecurityInfo()

    security.declarePrivate('after_setObject')
    def after_setObject(self):
        self.giveEditRights()

    security.declarePrivate('getEditRoles')
    def getEditRoles(self):
        # returns a list of roles with the edit permission
        return [role['name'] for role in self.rolesOfPermission(PERMISSION_EDIT_OBJECTS) if role['selected']]

    security.declarePrivate('giveEditRights')
    def giveEditRights(self):
        # make sure the contributor is owner and give edit permission to the owner
        roles = self.getEditRoles()
        self.manage_setLocalRoles(self.contributor, ['Owner'])
        if 'Owner' not in roles: roles.append('Owner')
        self.manage_permission(PERMISSION_EDIT_OBJECTS, roles, acquire=1)

    security.declarePrivate('takeEditRights')
    def takeEditRights(self):
        # remove edit rights
        roles = self.getEditRoles()
        if 'Owner' in roles:
            roles.remove('Owner')
            self.manage_permission(PERMISSION_EDIT_OBJECTS, roles, acquire=1)

    def get_schema_helper(self, lang=None):
        if lang is None:
            lang = self.gl_get_selected_language()
        local_properties = self._get_schema().listPropNames(local=True)

        schema = self._get_schema()

        def get_value(prop_name):
            val = self.getSession(prop_name, '')
            if val != '':
                widget = schema.getWidget(prop_name)
                prop_type = widget.getDataType()
                return prop_type(val)

            if prop_name in local_properties:
                return self.getLocalProperty(prop_name, lang)
            else:
                return getattr(self, prop_name, '')

        return SchemaFormHelper(self._get_schema(), self, get_value)

    security.declarePrivate('process_submitted_form')
    def process_submitted_form(self, REQUEST_form, _lang=None, _all_values=True, _override_releasedate=None):
        """
        take our data from the REQUEST object; if it's OK then save it,
        else return errors.
        """
        # TODO: need a method that saves schema properties on an object
        # directly (without passing through widget.parseFormData methods)
        schema = self._get_schema()
        form_data, form_errors = schema.processForm(REQUEST_form, _all_values)

        if _override_releasedate is not None:
            form_errors.pop('releasedate', '')
            form_data['releasedate'] = _override_releasedate

        have_errors = bool(sum(len(err) for err in form_errors.values()))

        if not have_errors:
            # all good; save the data

            if self.hasVersion():
                target = self.version
                self._p_changed = 1
            else:
                target = self

            target._change_schema_properties(_lang=_lang, **form_data)

            target.updateDynamicProperties(self.processDynamicProperties(
                self.meta_type, REQUEST_form), _lang)

        return form_errors

    security.declarePrivate('_prepare_error_response')
    def _prepare_error_response(self, REQUEST, form_errors, REQUEST_form):
        self.setSessionErrors(['The form contains errors. Please correct them and try again.'])
        for key, value in form_errors.iteritems():
            if value:
                self.setSession('%s-errors' % key, '; '.join(value))
        for key in self._get_schema().listPropNames():
            self.setSession(key, REQUEST_form.get(key, ''))

    security.declarePrivate('switch_content_to_language')
    def switch_content_to_language(self, old_lang, new_lang):
        if self.hasVersion():
            target = self.version
            self._p_changed = 1
        else:
            target = self

        local_properties = self._get_schema().listPropNames(local=True)
        for prop_name in local_properties:
            prop_value = target.getLocalProperty(prop_name, old_lang)
            target._setLocalPropValue(prop_name, new_lang, prop_value)
            target._setLocalPropValue(prop_name, old_lang, '')

    def get_meta_label(self):
        if self.meta_type == 'Naaya Folder':
            # TODO: port NyFolder to schema, so we can remove this special case
            return self.meta_label
        try:
            return self._get_schema().title_or_id()
        except AttributeError:
            return self.meta_label

    def object_submitted_message(self, REQUEST):
        if self.approved:
            self.setSessionInfo(['Item added'])
        elif self.checkPermissionPublishObjects():
            self.setSessionInfo(['Item added (unapproved)'])
        else:
            self.setSessionInfo(['The administrator will analyze your request and you will be notified about the result shortly.'])
        return REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url())

    def _version_status(self):
        # return version status
        if self.checkPermissionEditObject():
            if self.isVersionable():
                if self.hasVersion():
                    if self.isVersionAuthor():
                        return True, False
                        #return 'versioned-mine, not-editable'
                    else:
                        return False, False
                        #return 'versioned-not-mine, not-editable'
                else:
                    return True, True
                    #return 'versionable, editable'
            else:
                return False, True
                #return 'not-versionable, editable'
        else:
            return False, False
            #return 'no-permission, not-editable'

    def version_status(self):
        version, editable = self._version_status()
        pt = PageTemplateFile('zpt/version_status', globals())
        return pt.__of__(self)(version=version, editable=editable)

InitializeClass(NyContentType)

def _null_getattr(key):
    """ Blank __getattr__ implementation that never returns values """
    raise AttributeError(key)

from ExtensionClass import Base
class ForceGetattr(Base):
    """
    Some properties (most notably "title") are set on the OFS.SimpleItem.Item
    class, which breaks our implementation of local properties. This class
    behaves much like Localizer's LocalAttribute, returning the proper value
    for the property.
    """
    def __init__(self, prop_name):
        self.prop_name = prop_name

    def __of__(self, obj):
        return obj.__getattr__(self.prop_name)

class NyContentData(NyProperties):
    """
    Base class for "zzz_item" classes - container for the actual data stored
    in Naaya content types.

    meta_type is always set because a NyZzz class either inherits from us
    (so 'self' is actually a NyZzz instance) or we aquire it (because we're a
    descendant of a NyZzz instance).
    """

    security = ClassSecurityInfo()

    title = ForceGetattr('title')

    # TODO: dirty hack: making sure all objects have the geo_location
    # and geo_type properties. (--alexm)
    geo_location = None
    geo_type = ''

    def __init__(self):
        NyProperties.__dict__['__init__'](self)

    def __getattr__(self, key):
        """
        we override __getattr__ so we can return localized properties
        """

        # if we find 'key' in the _local_properties dictionary, this means we
        # have a local property
        if '_local_properties' in self.__dict__ and key in self._local_properties:
            return self.getLocalAttribute(key)

        # we import NyAttributes here to avoid import loop problems
        from Products.NaayaBase.NyAttributes import NyAttributes

        # calling NyAttributes.__getattr__ by hand: Localizer's __getattr__ does not
        # play nice and will not forward the call, so we do it here.
        if isinstance(self, NyAttributes):
            try:
                return NyAttributes.__getattr__(self, key)
            except AttributeError:
                pass
        return getattr(super(NyContentData, self), '__getattr__', _null_getattr)(key)

    def _get_schema(self):
        """ Fetch the schema for this object type """
        return self.getSite()._getOb(ID_SCHEMATOOL).getSchemaForMetatype(self.meta_type)

    def prop_details(self, prop_name, lang=None):
        """
        return property label, value and other info; useful for index_html views
        """
        if prop_name == 'contributor':
            authTool = self.getAuthenticationTool()
            value = authTool.getUserFullNameByID(self.contributor)
            label = 'Contributor'
            visible = self.display_contributor
        else:
            schema = self._get_schema()
            widget = schema.getWidget(prop_name)
            label = widget.title
            visible = widget.visible
            if widget.localized:
                value = self.getLocalProperty(prop_name, lang)
            else:
                value = getattr(self, prop_name)

        return {'label': label, 'visible': visible, 'value': value,
            'show': bool(visible and value)}

    _content_prop_tr = PageTemplateFile('zpt/content_prop_tr', globals())
    def prop_display_tr(self, prop_name, lang=None, **kwargs):
        """
        Display a property of this object (only if it's not hidden) with the
        correct label using <tr> markup
        """
        data = self.prop_details(prop_name, lang)
        data.update(kwargs)

        if data.get('as_href', False) and data['value'] in ['', 'http://']:
            data['visible'] = False

        if data['visible']:
            if prop_name == 'releasedate':
                data['value'] = self.utShowDateTime(data['value'])

            data.setdefault('as_href', False)
            data.setdefault('rel', None)
            return self._content_prop_tr(**data)

        else:
            return ''

    def prop_value_or_none(self, prop_name, lang=None):
        details = self.prop_details(prop_name, lang)
        if details['visible']:
            return details['value']
        else:
            return None

    def _change_schema_properties(self, _lang=None, **kwargs):
        """
        Change specific properties of this object

        Note: this method should only be called by process_submitted_form of NyContentType
        """
        if _lang is None:
            _lang = self.gl_get_selected_language()
        schema = self._get_schema()
        local_properties = schema.listPropNames(local=True)

        for prop_name, prop_value in kwargs.iteritems():
            widget = schema.getWidget(prop_name)
            prop_type = widget.getDataType()
            if not isinstance(prop_value, prop_type) and prop_value is not None:
                prop_value = prop_type(prop_value)
            if widget.localized:
                self._setLocalPropValue(prop_name, _lang, prop_value)
            else:
                setattr(self, prop_name, prop_value)

        self.updatePropertiesFromGlossary(_lang)
        self._p_changed = 1
        self.recatalogNyObject(self)

    security.declarePrivate('copy_naaya_properties_from')
    def copy_naaya_properties_from(self, other):
        schema = self._get_schema()
        local_properties = schema.listPropNames(local=True)

        for prop_name in schema.listPropNames():
            if prop_name in local_properties:
                pass # these will be copied a bit later in bulk
            else:
                setattr(self, prop_name, getattr(other, prop_name))

        # copy Localizer's data structures
        self._local_properties = deepcopy(other._local_properties)
        self._local_properties_metadata = deepcopy(other._local_properties_metadata)

        # copy "Dynamic Properties"
        self.setProperties(deepcopy(other.getProperties()))

    security.declarePrivate('dump_data')
    def dump_data(self):
        schema = self._get_schema()
        local_properties = schema.listPropNames(local=True)
        for prop_name in schema.listPropNames():
            if prop_name in local_properties:
                localdict = self._local_properties.get(prop_name, {})
                value = dict( (lang, localdict[lang][0]) for lang in localdict)
            else:
                value = getattr(self, prop_name)
            yield prop_name, value

    security.declareProtected(view, 'geo_latitude')
    def geo_latitude(self):
        if self.geo_location is None:
            raise AttributeError
        if self.geo_location.lat is None:
            raise AttributeError
        return self.geo_location.lat

    security.declareProtected(view, 'geo_longitude')
    def geo_longitude(self):
        if self.geo_location is None:
            raise AttributeError
        if self.geo_location.lon is None:
            raise AttributeError
        return self.geo_location.lon

    security.declareProtected(view, 'geo_address')
    def geo_address(self):
        if self.geo_location is None:
            return ''
        if self.geo_location.address is None:
            return ''
        return self.geo_location.address

    security.declarePrivate(view, 'title_utf8')
    def title_utf8(self):
        if not isinstance(self.title, basestring):
            return self.title
        return self.title.encode('utf-8')

InitializeClass(NyContentData)
