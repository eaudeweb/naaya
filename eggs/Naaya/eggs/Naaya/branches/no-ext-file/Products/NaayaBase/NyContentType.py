from copy import deepcopy
import logging

from AccessControl import ClassSecurityInfo
from AccessControl.Permission import Permission
from AccessControl.Permissions import view
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import implements
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.event import notify
from DateTime import DateTime
from DateTime.interfaces import DateError, SyntaxError

from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaBase.constants import PERMISSION_DELETE_OBJECTS
from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaBase.NyProperties import update_translation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaCore.constants import ID_SCHEMATOOL
from naaya.content.base.interfaces import INyContentObject
from naaya.core.zope2util import parents_in_site_path

log = logging.getLogger(__name__)

NY_CONTENT_BASE_SCHEMA = {
    'title': {'sortorder':10, 'widget_type':'String', 'label':'Title',
              'required':True, 'localized':True},
    'description': { 'sortorder':20, 'widget_type':'TextArea',
                     'label':'Description', 'localized':True,
                     'tinymce':True},
    'geo_location': {'sortorder':24, 'widget_type':'Geo', 'data_type':'geo',
                     'label':'Geographical location', 'visible':False},
    'geo_type': {'sortorder':26, 'widget_type':'GeoType', 'data_type':'str',
                 'label':'Geographical location type', 'visible':False},
    'coverage': {'sortorder':30, 'widget_type':'Glossary',
                 'label':'Geographical coverage', 'glossary_id':'coverage',
                 'localized':True},
    'keywords': {'sortorder':40, 'widget_type':'Glossary', 'label':'Keywords',
                 'glossary_id':'keywords', 'localized':True},
    'sortorder': {'sortorder':50, 'widget_type':'String', 'data_type':'int',
                  'default':'100', 'label':'Sort order', 'required':True,
                  'visible':False},
    'releasedate': {'sortorder':60, 'widget_type':'Date', 'data_type':'date',
                    'label':'Release date', 'required':True},
    'discussion': {'sortorder':70, 'widget_type':'Checkbox', 'data_type':'int',
                   'label':'Open for comments'},
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

    def form_items_add(self):
        return self.form_items(add=True)

    def _get_value(self, prop_name, add):
        if add and prop_name == 'coverage':
            value = getattr(self.context, 'default_geographical_coverage', '')
            if value:
                return value
        if self.value_callback:
            value = self.value_callback(prop_name)
            if value is not None:
                return value
        widget = self.schema.getWidget(prop_name)
        prop_type = widget.getDataType()
        val = self.context.getSession(prop_name, '')
        if prop_type is None:
            return val or None
        if val in ('', None):
            if prop_name == 'releasedate':
                # special case for releasedate - default to "today"
                return DateTime().strftime('%d/%m/%Y')
            elif widget.default not in (None, ''):
                if prop_type is DateTime:
                    return prop_type(widget.default, datefmt='international')
                else:
                    return prop_type(widget.default)
            else:
                if prop_type is DateTime:
                    return ''
                else:
                    return prop_type()
        else:
            try:
                return prop_type(val)
            except (ValueError, DateError, SyntaxError):
                # in case the string is malformed
                # added DateError for DateTime errors
                return prop_type()

    def _get_renderer(self, prop_name, widget, add):
        value = self._get_value(prop_name, add)
        context = self.context
        errors = self.context.getSession('%s-errors' % prop_name, None)
        def render():
            return widget.render_html(value=value,
                                      context=context,
                                      errors=errors)
        return render

    def form_items(self, add=False):
        for widget in self.schema.listWidgets():
            prop_name = widget.prop_name()
            yield {'name': prop_name, 'html': self._get_renderer(prop_name,
                    widget, add=add)}

    def del_schema_session_values(self):
        schema_prop_names = self.schema.listPropNames()
        for key in self.context.REQUEST.SESSION.keys():
            # We remove anything that ends in '-errors', not just schema
            # errors. This is not ideal, but content types sometimes expect
            # their own non-schema errors to be removed by us.
            if key.endswith('-errors'):
                self.context.delSession(key)
            # we must delete "propname" keys and keys starting with "propname."
            # SchemaProps can have properties of their own (eg Geo, Interval)
            if key.split('.', 1)[0] in schema_prop_names:
                self.context.delSession(key)

    def get_meta_label(self):
        return self.schema.title_or_id()


def get_schema_helper_for_metatype(context, meta_type, value_callback=None):
    schema = context.getSite()._getOb(ID_SCHEMATOOL).getSchemaForMetatype(meta_type)
    return SchemaFormHelper(schema, context, value_callback)


class NyContentType(object):
    """
    Base class for NyZzz classes - wrapper for NyContentData instances
    that handle editing, displaying, etc.
    """

    implements(INyContentObject, IAttributeAnnotatable)

    security = ClassSecurityInfo()

    security.declarePrivate('after_setObject')
    def after_setObject(self):
        self.giveEditRights()

    security.declarePrivate('getEditRoles')
    def getEditRoles(self):
        # returns a list of roles with the edit permission
        return [role['name'] for role in
                self.rolesOfPermission(PERMISSION_EDIT_OBJECTS)
                if role['selected']]

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

    security.declarePrivate('dont_inherit_view_permission')
    def dont_inherit_view_permission(self):
        permission = Permission(view, (), self)
        roles = permission.getRoles()
        roles = tuple(set(roles) | set(['Manager', 'Administrator', 'Owner']))
        permission.setRoles(roles)

    security.declarePrivate('inherit_view_permission')
    def inherit_view_permission(self):
        permission = Permission(view, (), self)
        roles = permission.getRoles()
        roles = list(roles)
        permission.setRoles(roles)

    security.declarePrivate('process_submitted_form')
    def process_submitted_form(self, REQUEST_form, _lang=None,
                               _all_values=True, _override_releasedate=None):
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

        return form_errors

    security.declarePrivate('_prepare_error_response')
    def _prepare_error_response(self, REQUEST, form_errors, REQUEST_form):
        self.setSessionErrorsTrans('The form contains errors. Please correct them and try again.')
        for key, value in form_errors.iteritems():
            if value:
                self.setSession('%s-errors' % key, '; '.join(value))
        schema = self._get_schema()
        for prop_name in schema.listPropNames():
            for key in REQUEST_form:
                if key == prop_name or key.startswith(prop_name+'.'):
                    widget = schema.getWidget(prop_name)
                    value = widget.convert_to_session(REQUEST_form[key])
                    self.setSession(key, value)

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
            self.setSessionInfoTrans('Item added')
        elif self.checkPermissionPublishObjects():
            self.setSessionInfoTrans('Item added (unapproved)')
        else:
            self.setSessionInfoTrans('The administrator will analyze your request and you will be notified about the result shortly.')
        return REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url())

    def version_status(self):
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

    # patch getVersionLocalProperty because some templates still use it
    def getVersionLocalProperty(self, id, lang):
        if isinstance(self, NyCheckControl):
            return NyCheckControl.getVersionLocalProperty(self, id, lang)
        else:
            return self.getLocalProperty(id, lang)

    set_content_rating = PageTemplateFile('zpt/set_content_rating', globals())

    def is_ratable(self):
        """returns the stars rating view if the content type is ratable"""

        schema = self.getSite().portal_schemas.getSchemaForMetatype(self.meta_type)
        return schema.is_ratable

    def can_be_seen(self):
        """
        Indicates if the current user has access to the current folder.
        """

        return self.checkPermission(view)

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteThis')
    def deleteThis(self, REQUEST=None):
        """ Delete the current object """

        user = getattr(REQUEST, 'AUTHENTICATED_USER', None)
        log.info("Deleting object %r (authenticated user: %r)", self, user)

        parent = self.aq_inner.aq_parent
        parent.manage_delObjects([self.getId()])

        if REQUEST is not None:
            title = self.title_or_id()
            self.setSessionInfoTrans('Item "${title}" deleted.', title=title)
            REQUEST.RESPONSE.redirect('%s/' % parent.absolute_url())

    security.declareProtected(view, 'is_geo_enabled')
    def is_geo_enabled(self):
        """ check if the current object is geo_enabled """

        schema_tool = self.getSchemaTool()
        schema = schema_tool.getSchemaForMetatype(self.meta_type)
        return schema_tool.content_type_info(schema)['geo_enabled']

    security.declarePrivate('notify_access_event')
    def notify_access_event(self, REQUEST, event_type='view'):
        """ Shortcut to easier call a view/download notify event for NyZzz """
        from Products.NaayaCore.AuthenticationTool.AuthenticationTool import is_anonymous
        if REQUEST and not is_anonymous(REQUEST.AUTHENTICATED_USER):
            if event_type == 'view':
                from naaya.content.base.events import NyContentObjectViewEvent
                event_factory = NyContentObjectViewEvent
            elif event_type == 'download':
                from naaya.content.base.events import NyContentObjectDownloadEvent
                event_factory = NyContentObjectDownloadEvent
            else:
                log.error("Unkown access event type %r", event_type)
                return None
            notify(event_factory(self, REQUEST.AUTHENTICATED_USER.getUserName()))

    security.declarePublic('pretty_path')
    def pretty_path(self):
        """
        Returns the object path in a breadcrumbs-like representation, relative
        to site - useful when referencing object, specially in Admin

        """
        parents = parents_in_site_path(self)
        if len(parents) > 1:
            parents.pop(0) # do not include site
        return " &raquo; ".join(parents)


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
        if self.hasLocalProperty(key):
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

    security.declareProtected(view, 'get_schema_helper')
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
                if prop_type is None:
                    return val or None
                else:
                    return prop_type(val)

            if prop_name in local_properties:
                return self.getLocalProperty(prop_name, lang)
            else:
                return getattr(self.aq_base, prop_name, '')

        return SchemaFormHelper(self._get_schema(), self, get_value)

    security.declareProtected(view, 'prop_exists')
    def prop_exists(self, prop_name):
        """
        The safe way to check whether a schema property exists on object.
        (bypasses properties from context throughout acquisition)
        E.g.
        <span tal:condition='here/topics'> may return true if you happen
        to have a 'topics' container in your context. Always use
        <span tal:condition='python:here.prop_exists('topics')'>

        """
        # TODO: maybe use AccessControl.ZopeGuards.guarded_getattr (in rstk)?
        return hasattr(self.aq_base, prop_name)

    security.declareProtected(view, 'prop_details')
    def prop_details(self, prop_name, lang=None):
        """
        return property label, value and other info; useful for index_html views
        """

        if prop_name == 'contributor':
            authTool = self.getAuthenticationTool()
            value = authTool.getUserFullNameByID(self.contributor)
            label = 'Contributor'
            visible = self.display_contributor or self.checkPermissionEditObject()
        else:
            schema = self._get_schema()
            widget = schema.getWidget(prop_name)
            label = widget.title
            if prop_name == 'releasedate':
                visible = widget.visible or self.checkPermissionEditObject()
            else:
                visible = widget.visible
            if widget.localized:
                value = self.getLocalProperty(prop_name, lang)
            else:
                value = getattr(self, prop_name)

        return {'label': label, 'visible': visible, 'value': value,
            'show': bool(visible and value)}

    _content_prop_tr = PageTemplateFile('zpt/content_prop_tr', globals())
    security.declareProtected(view, 'prop_display_tr')
    def prop_display_tr(self, prop_name, lang=None, **kwargs):
        """
        Display a property of this object (only if it's not hidden) with the
        correct label using <tr> markup
        """

        data = self.prop_details(prop_name, lang)
        data.update(kwargs)

        if not getattr(self.aq_base, prop_name, ''):
            return ''

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

    security.declareProtected(view, 'prop_value_or_none')
    def prop_value_or_none(self, prop_name, lang=None):
        details = self.prop_details(prop_name, lang)
        if details['visible']:
            return details['value']
        else:
            return None

    def _change_schema_properties(self, _lang=None, **kwargs):
        """
        Change specific properties of this object
        """

        #TODO This method should be formalised as an API method
        if _lang is None:
            _lang = self.gl_get_selected_language()
        schema = self._get_schema()
        local_properties = schema.listPropNames(local=True)

        for prop_name, prop_value in kwargs.iteritems():
            widget = schema.getWidget(prop_name)
            prop_type = widget.getDataType()
            if prop_type is not None:
                if not isinstance(prop_value, prop_type) and prop_value is not None:
                    prop_value = prop_type(prop_value)

            if widget.localized:
                prev_prop_value = self.getLocalProperty(prop_name, _lang)
                new_prop_value = widget.new_value(prev_prop_value, prop_value)
                self._setLocalPropValue(prop_name, _lang, new_prop_value)
            else:
                if prop_type is None:
                    default = None
                else:
                    default = prop_type()
                prev_prop_value = getattr(self.aq_base, prop_name, default)
                new_prop_value = widget.new_value(prev_prop_value, prop_value)
                setattr(self, prop_name, new_prop_value)

            if widget.meta_type == 'Naaya Schema Glossary Widget':
                glossary = widget.get_glossary()
                if glossary is not None:
                    update_translation(self, prop_name,
                                       glossary, _lang, prev_prop_value,
                                       widget.separator)

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

    security.declareProtected(view, 'title_utf8')
    def title_utf8(self):
        if not isinstance(self.title, basestring):
            return self.title
        return self.title.encode('utf-8')

InitializeClass(NyContentData)
