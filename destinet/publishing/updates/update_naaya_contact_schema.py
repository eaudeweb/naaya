from Products.naayaUpdater.updates import UpdateScript


class ChangeNaayaContactSchema(UpdateScript):
    """ Migration: upgrade the NaayaContact schema in portal_schemas
    """

    title = "Destinet: migrate the NaayaContact schema"
    creation_date = 'Dec 18, 2013'
    authors = ['Tiberiu ichim']
    description = ("Add the necessary fields")

    def _update(self, portal):
        schema = portal['portal_schemas']['NyContact']
        schema['geo_type-property'].required = False
        schema['geo_type-property'].title = "DEPRECATED: Category"

        widget = schema.addWidget('category-organization', widget_type="GeoType", data_type='str', required=True)
        widget.title = "Organization Category"
        widget.sortorder = 27
        widget.custom_template = "portal_forms/schemawidget-category-organization"
        widget.help_text = "What type of organization are you?"

        widget = schema.addWidget('category-marketplace', widget_type="GeoType", data_type='str', required=False)
        widget.title = "List yourself in DestINet's Sustainable Tourism Global Market Place"
        widget.sortorder = 28
        widget.custom_template = "portal_forms/schemawidget-category-marketplace"
        widget.help_text = "Do you wish to register a sustainable tourism business activity or service in the global green market place?"

        widget = schema.addWidget('category-supporting-solutions', widget_type="GeoType", data_type='str', required=False)
        widget.title = "Supporting Solutions"
        widget.sortorder = 29
        widget.custom_template = "portal_forms/schemawidget-category-supporting-solutions"
        widget.help_text = "Do you offer services to support sustainable tourism development?"

        return True
