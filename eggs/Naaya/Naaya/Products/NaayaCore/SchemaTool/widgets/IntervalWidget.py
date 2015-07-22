from datetime import datetime

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget
from naaya.core.custom_types import Interval
from naaya.core.exceptions import i18n_exception

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


    def normalize_date(self, date, time, all_day, name):
        """ Used by parseFormData """
        if date is None:
            return date
        try:
            ds = map(int, date.split("/"))
            if all_day is True:
                return datetime(ds[2], ds[1], ds[0])
            else:
                (h, m) = map(int, time.split(":"))
                return datetime(ds[2], ds[1], ds[0], h, m)
        except Exception, e:
            raise i18n_exception(WidgetError,
                                 'Bad value (${date}, ${time}) for ${who}',
                                 date=repr(date), time=repr(time), who=name)

    def parseFormData(self, data):
        if self.isEmptyDatamodel(data):
            return None

        if isinstance(data, Interval):
            return data

        if not isinstance(data, dict):
            raise i18n_exception(WidgetError,
                                 'Expected multiple values for "${title}"',
                                 title=self.title)

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

            if None in (start_date, end_date):
                raise i18n_exception(WidgetError,
                                     'Start time (date) and End time (date) ' +
                                     'must both have values')
            elif all_day is False and None in (start_time, end_time):
                raise i18n_exception(WidgetError,
                                     'Start time (hh:mm) and End time (hh:mm)' +
                                 ' must both have values when all_day is False')
            else:
                start_date = self.normalize_date(start_date, start_time,
                                                 all_day, "Start Time")
                end_date = self.normalize_date(end_date, end_time, all_day,
                                          "End Time")

            return Interval(start_date, end_date, all_day)
        except ValueError, e:
            raise i18n_exception(WidgetError, str(e))

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
        # right assertion used for some old empty Interval objects
        # saved with all_day = True which failed first assertion
        if value == Interval() or value.start_date is None:
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
