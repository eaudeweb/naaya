""" Core methods for dealing with registration in Destinet """
from Products.NaayaCore.SchemaTool.widgets.Widget import WidgetError

from destinet.registration.constants import WIDGET_NAMES


def validate_widgets(contact_schema, registration_schema, form):
    """
    This is almost the same code and logic from
    :meth:`~Products.NaayaCore.SchemaTool.Schema.Schema.processForm`

    """
    form_data = {}
    form_errors = {}
    widgets = [contact_schema["%s-property" % w] for w in WIDGET_NAMES]
    widgets.extend(registration_schema.objectValues())

    any_of = ["category-marketplace",
              "category-supporting-solutions"]

    extra_required = ["landscape_type", "topics"]

    # if any field in any_of has value,
    # then all widgets in extra_required are required
    required_flag = False

    for widget in widgets:
        field_name = widget.prop_name()

        if field_name in form:
            raw_value = form[field_name]
        elif widget.multiple_form_values:
            raw_value = {}
            for key, value in form.iteritems():
                if key.startswith(field_name + '.'):
                    raw_value[key[len(field_name) + 1:]] = value
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

        if field_name in any_of and value:
            required_flag = True

        if (field_name in extra_required) and required_flag and not value:
            errors.append(u'Value required for "%s"' % widget.title)

        if errors:
            form_errors[field_name] = errors

    return form_data, form_errors


def prepare_error_response(context, contact_schema, register_schema,
                           form_errors, req_form):
    """
    Almost the same as
    :meth:`~Products.NaayaBase.NyContentType.\
    NyContentType._prepare_error_response`
    but we have our own list of widgets, not a schema.

    """
    if form_errors:
        context.setSessionErrorsTrans('The form contains errors. '
                                      'Please correct them and try again.')
    for key, value in form_errors.iteritems():
        if value:
            context.setSession('%s-errors' % key, '; '.join(value))

    for prop_name in WIDGET_NAMES:
        for key in req_form:
            if key == prop_name or key.startswith(prop_name + '.'):
                widget = contact_schema.getWidget(prop_name)
                value = widget.convert_to_session(req_form[key])
                context.setSession(key, value)

    for widget in register_schema.objectValues():
        prop_name = widget.prop_name()
        for key in req_form:
            if key == prop_name or key.startswith(prop_name + '.'):
                value = widget.convert_to_session(req_form[key])
                context.setSession(key, value)


def handle_groups(ob, req_form):
    """
    Assign roles, set keywords, recatalog.

    """
    site = ob.getSite()
    groups = req_form.get('groups', [])
    for group in groups:
        if group == 'european-ecotourism-network':
            username = req_form['username']
            try:
                site.admin_addroles([username], ['EEN Member', 'Contributor'],
                                    '', send_mail=True)
            except AttributeError:
                pass    # This happens when user is root acl user
            lang = ob.gl_get_selected_language()
            ob._setLocalPropValue('keywords', lang,
                                  'European Ecotourism Network')
            ob.recatalogNyObject(ob)
