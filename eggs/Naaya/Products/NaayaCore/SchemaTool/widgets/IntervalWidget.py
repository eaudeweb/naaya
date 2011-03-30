from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget
from naaya.core.custom_types import Interval

def addIntervalWidget(container, id="", title="Interval Widget", REQUEST=None, **kwargs):
    """ Contructor for Interval widget"""
    return manage_addWidget(IntervalWidget, container, id, title, REQUEST, **kwargs)

class IntervalWidget(Widget):
    """ Interval Widget """

    meta_type = "Naaya Schema Interval Widget"
    meta_label = "Start and end time, optionally including time of day"
    meta_description = "Represents an interval on the calendar (e.g. for an event)"
    meta_sortorder = 200

    # Constructor
    _constructors = (addIntervalWidget,)

    multiple_form_values = ('start_date', 'start_time', 'end_date', 'end_time',
                            'all_day')
    default = None


    def parseFormData(self, data):
        if self.isEmptyDatamodel(data):
            return None

        if isinstance(data, Interval):
            return data

        if not isinstance(data, dict):
            raise WidgetError('Expected multiple values for "%s"' % self.title)

        try:
            start_date = data.get('start_date', None)
            if not start_date:
                start_date = None
            end_date = data.get('end_date', None)
            if not end_date:
                end_date = None
            start_time = data.get('start_time', None)
            if not start_time:
                start_time = None
            end_time = data.get('end_time', None)
            if not end_time:
                end_time = None
            all_day = data.get('all_day', False)
            if all_day:
                all_day = True
            return Interval(start_date, start_time, end_date, end_time, all_day)
        except ValueError, e:
            raise WidgetError(str(e))

    def isEmptyDatamodel(self, value):
        if isinstance(value, dict):
            return ''.join(map(str, value.values())) == ''
        else:
            return value in (None, '', Interval())

    def convertValue(self, value):
        if not (value is None or isinstance(value, Interval)):
            raise WidgetError('Bad value for Interval: %s' % repr(value))
        elif value == Interval():
            return None
        else:
            return value

    def _convert_to_form_string(self, value):
        """
        Turn data to string as seen in form
        """
        if value == Interval():
            return None
        else:
            return {'start_date': value.start_date.strftime('%d/%m/%Y'),
                    'start_time': value.start_date.strftime('%H:%M'),
                    'end_date': value.end_date.strftime('%d/%m/%Y'),
                    'end_time': value.end_date.strftime('%H:%M'),
                    'all_day': ['', '1'][value.all_day is True]}

    hidden_template = PageTemplateFile('../zpt/property_widget_hidden_interval', globals())

    template = PageTemplateFile('../zpt/property_widget_interval', globals())

InitializeClass(IntervalWidget)
