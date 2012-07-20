""" Core methods for dealing with registration in Destinet """
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.SchemaTool.widgets.Widget import WidgetError

from destinet.registration.constants import WIDGET_NAMES


def validate_widgets(schema, form):
    """
    This is almost the same code and logic from
    :meth:`~Products.NaayaCore.SchemaTool.Schema.Schema.processForm`

    """
    form_data = {}
    form_errors = {}
    widgets = [schema["%s-property" % w] for w in WIDGET_NAMES ]
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

def prepare_error_response(context, schema, form_errors, req_form):
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
                widget = schema.getWidget(prop_name)
                value = widget.convert_to_session(req_form[key])
                context.setSession(key, value)
