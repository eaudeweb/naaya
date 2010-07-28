from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateDynamicProp2Schema(UpdateScript):
    """ """
    title = 'Convert DynamicProperties to SchemaTool'
    authors = ['Alexandru Plugaru']
    description = 'Migrate all DynamicPropertiesTool properties to SchemaTool '
    'widgets'
    priority = PRIORITY['HIGH']
    creation_date = 'Jan 01, 2010'
    #Dynamic prop => SchemaWidget Widget, datatype
    relations = {
        "boolean": ("Checkbox", 'bool', ),
        "string": ("String", 'str', ),
        "date": ("Date", 'date', ),
        "integer": ("String", 'int', ),
        "float": ("String", 'float', ),
        "text": ("TextArea", 'str', ),
        "selection": ("Select", 'list', ),
    }


    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, '_update')
    def _update(self, portal):
        """ Check all dynamic properties and create an equivalent widget in
        SchemaTool. After deleting/adding widgets.

        """
        schema_tool = portal.getSchemaTool()
        dynamic_prop_tool = portal.getDynamicPropertiesTool()
        portlets_tool = portal.getPortletsTool()

        for dynamic_prop in dynamic_prop_tool.objectValues():
            meta_type = dynamic_prop.id
            schema = schema_tool.getSchemaForMetatype(meta_type)
            if schema is None: #If no schema is found then skip this content
                continue

            for prop in dynamic_prop.getDynamicProperties():
                widget_type, data_type = self.relations[prop.type]
                try:
                    schema.getWidget(prop.id)
                except KeyError:
                    args = dict(
                        label=prop.name,
                        data_type=data_type,
                        widget_type=widget_type,
                        sortorder=int(prop.order) + 300,
                        required=bool(prop.required),
                        default=prop.defaultvalue
                    )
                    if prop.type == 'selection':
                         #Selection list does not exist
                        if isinstance(prop.values, str):
                            if not len(portal.get_list_nodes(prop.id)):
                                #Create an RefTree
                                portlets_tool.manage_addRefTree(prop.id)
                                reftree_ob = portlets_tool._getOb(prop.id)
                                values = prop.values.replace("\r", '')
                                selection_items = filter(None, [unicode(x).strip()
                                                                for x in values.split("\n")])
                                for item in selection_items:
                                    reftree_ob.manage_addRefTreeNode(str(item),
                                                                     item)
                            args.update({'list_id': prop.id})
                        elif isinstance(prop.values, dict): #Set up existing
                            args.update({'list_id': prop.values.keys()[0]})
                        else:
                            raise ValueError('unexpected values type')
                    widget = schema.addWidget(prop.id, **args)
                    self.log.debug('Created SchemaTool widget %r for %s'
                                   % (prop.id, meta_type))

                #Deleting dynamic prop from the tool
                dynamic_prop.manageDeleteDynamicProperties(prop.id)
                self.log.debug('Deleted dynamic prop %r for %s'
                                   % (prop.id, meta_type))
            #Deleting dynamic moved dynamic property if it's empty
            if not len(dynamic_prop.getDynamicProperties()):
                dynamic_prop_tool.manage_delObjects(dynamic_prop.id)
                self.log.debug('Deleted dynamic property %s', meta_type)
        return True
