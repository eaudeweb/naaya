""" Core methods for dealing with registration in Destinet """
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.SchemaTool.widgets.Widget import WidgetError
from naaya.core.zope2util import path_in_site
from naaya.content.pointer.pointer_item import addNyPointer

from destinet.registration.constants import WIDGET_NAMES, USER_GROUPS


def validate_widgets(contact_schema, registration_schema, form):
    """
    This is almost the same code and logic from
    :meth:`~Products.NaayaCore.SchemaTool.Schema.Schema.processForm`

    """
    form_data = {}
    form_errors = {}
    widgets = [contact_schema["%s-property" % w] for w in WIDGET_NAMES ]
    widgets.extend(registration_schema.objectValues())
    for widget in widgets:
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
            if widget.data_type == 'list':
                value = []
            else:
                value = widget.default

        errors = []
        try:
            widget.validateDatamodel(value)
            widget_value = widget.parseFormData(value)
            form_data[field_name] = widget.convertValue(widget_value)
        except WidgetError, e:
            errors.append(str(e))
            form_data[field_name] = value

        if errors:
            form_errors[field_name] = errors
    return form_data, form_errors

def prepare_error_response(context, contact_schema, register_schema,
                           form_errors, req_form):
    """
    Almost the same as
    :meth:`~Products.NaayaBase.NyContentType.NyContentType._prepare_error_response`
    but we have our own list of widgets, not a schema.

    """
    if form_errors:
        context.setSessionErrorsTrans('The form contains errors. Please correct them and try again.')
    for key, value in form_errors.iteritems():
        if value:
            context.setSession('%s-errors' % key, '; '.join(value))

    for prop_name in WIDGET_NAMES:
        for key in req_form:
            if key == prop_name or key.startswith(prop_name+'.'):
                widget = contact_schema.getWidget(prop_name)
                value = widget.convert_to_session(req_form[key])
                context.setSession(key, value)

    for widget in register_schema.objectValues():
        prop_name = widget.prop_name()
        for key in req_form:
            if key == prop_name or key.startswith(prop_name+'.'):
                value = widget.convert_to_session(req_form[key])
                context.setSession(key, value)

def place_pointer_to_contact(ob, pointer_parent):
    """
    Very much like :func:~destinet.publishing.subscribers.place_pointers:

    """
    props = {
        'title': ob.title,
        'description': getattr(ob, 'description', ''),
        'topics': ob.__dict__.get('topics', []),
        'target-groups': ob.__dict__.get('target-groups', []),
        'geo_location.lat': '',
        'geo_location.lon': '',
        'geo_location.address': '',
        'geo_type': getattr(ob, 'geo_type', ''),
        'coverage': ob.__dict__.get('coverage', ''),
        'keywords': ob.__dict__.get('keywords', ''),
        'sortorder': getattr(ob, 'sortorder', ''),
        'redirect': True,
        'pointer': path_in_site(ob)
    }
    if ob.geo_location:
        if ob.geo_location.lat:
            props['geo_location.lat'] = unicode(ob.geo_location.lat)
        if ob.geo_location.lon:
            props['geo_location.lon'] = unicode(ob.geo_location.lon)
        if ob.geo_location.address:
            props['geo_location.address'] = ob.geo_location.address
    if not props['sortorder']:
        props['sortorder'] = '200'

    p_id = addNyPointer(pointer_parent, ob.getId(), contributor=ob.contributor, **props)
    pointer = pointer_parent._getOb(p_id, None)
    if pointer:
        if ob.approved:
            pointer.approveThis(1, ob.contributor)
        else:
            pointer.approveThis(0, None)
        return pointer

def handle_groups(ob, req_form):
    """
    If user selected a group to be member/user of, then a pointer must
    be created to his profile (hist contact object) in folder of each
    selected group.

    """
    site = ob.getSite()
    groups = req_form.get('groups', [])
    for group in groups:
        if group == 'european-ecotourism-network':
            username = req_form['username']
            site.admin_addroles([username], ['EEN Member', 'Contributor'],
                                '', send_mail=True)
            lang = ob.gl_get_selected_language()
            ob._setLocalPropValue('keywords', lang,
                                  'European Ecotourism Network')
            ob.recatalogNyObject(ob)
        if group in USER_GROUPS:
            pointer_location = site.unrestrictedTraverse(USER_GROUPS[group])
            place_pointer_to_contact(ob, pointer_location)
