# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Product imports
from Widget import Widget, WidgetError, manage_addWidget


def addDateWidget(container, id="", title="Date Widget", REQUEST=None, **kwargs):
    """ Contructor for Date widget"""
    return manage_addWidget(DateWidget, container, id, title, REQUEST, **kwargs)

class DateWidget(Widget):
    """Date Widget"""

    meta_type = "Naaya Schema Date Widget"
    meta_label = "Date"
    meta_description = "A valid date chosen by the user"
    meta_sortorder = 200

    _properties = Widget._properties + ()

    # Constructor
    _constructors = (addDateWidget,)

    default = DateTime().strftime('%d/%m/%Y')

    def parseFormData(self, value):
        """Get datamodel from form"""
        if not value:
            return None
        if len(value.strip().split('-')) == 3:
            try:
                year, month, day = [int(i) for i in value.strip().split('-')]
                value = DateTime(year, month, day)
            except:
                raise WidgetError('Invalid date string for "%s"' % self.title)
        else:
            try:
                day, month, year = [int(i) for i in value.strip().split('/')]
                value = DateTime(year, month, day)
            except:
                try:
                    year, month, day = [int(i) for i in value.strip().split('/')]
                    value = DateTime(year, month, day)
                except:
                    raise WidgetError('Invalid date string for "%s"' % self.title)
        return value

    def _convert_to_form_string(self, value):
        if isinstance(value, DateTime):
            value = value.strftime('%d/%m/%Y')
        return value

    template = PageTemplateFile('../zpt/property_widget_date', globals())

InitializeClass(DateWidget)
