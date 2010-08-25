from Products.naayaUpdater.updates import UpdateScript

class UpdateWidget(UpdateScript):
    """  """
    id = 'update_widget'
    title='Changes a select widget to a multiple select widget **hotfix'
    description=''

    def _update(self, portal):
        """ """
        meta_types = ['Naaya Event', 'Naaya News', 'Naaya Contact',
                     'Naaya GeoPoint', 'Naaya URL', 'Naaya Media File',
                     'Naaya Publication', 'Naaya File']
        widget_id = 'landscape_type'

        schema_tool = portal.getSchemaTool()

        for meta_type in meta_types:
            schema = schema_tool.getSchemaForMetatype(meta_type)
            widget = schema.getWidget(widget_id)
            if widget.get_widget_type() == 'Select':
                widget_properties = {
                    'label': widget.title,
                    'data_type': 'list',
                    'widget_type': 'SelectMultiple',
                    'sortorder': widget.sortorder,
                    'required': widget.required,
                    'default': widget.default,
                    'localized': True,
                    'list_id': widget.list_id,
                }
                schema.manage_delObjects([widget.id])
                self.log.debug('Delete old widget %r in %r', widget_id, meta_type)
                schema.addWidget(widget_id, **widget_properties)
                self.log.debug('Created new widget %r in %r', widget_id, meta_type)
        return True
