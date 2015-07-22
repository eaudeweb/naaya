from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addGeoTypeWidget(container, id="", title="Select Widget", REQUEST=None, **kwargs):
    """ Contructor for Select widget"""
    return manage_addWidget(GeoTypeWidget, container, id, title, REQUEST, **kwargs)

class GeoTypeWidget(Widget):
    """ Select Widget """

    meta_type = "Naaya Geo Type Widget"
    meta_label = "Select map marker"
    meta_description = "Value selection from list of map markers"
    meta_sortorder = 150

    # Constructor
    _constructors = (addGeoTypeWidget,)

    def _convert_to_form_string(self, value):
        if isinstance(value, int):
            value = str(value)
        return value

    def convert_from_user_string(self, value):
        """ Convert a user-readable string to a value that can be saved """
        if value == '':
            return ''
        geo_map_tool = self.getSite().getGeoMapTool()
        for symbol in geo_map_tool.getSymbolsList():
            if value.strip().lower() == symbol.title.lower():
                return symbol.id
        raise ValueError('Could not convert value %s' % repr(value))

    def convert_to_user_string(self, value):
        """ Convert a database value to a user-readable string """
        if value == '':
            return u''
        geo_map_tool = self.getSite().getGeoMapTool()
        for symbol in geo_map_tool.getSymbolsList():
            if value == symbol.id:
                return symbol.title
        return u'ERROR: no symbol with id %s' % repr(value)

    template = PageTemplateFile('../zpt/property_widget_geo_type', globals())
