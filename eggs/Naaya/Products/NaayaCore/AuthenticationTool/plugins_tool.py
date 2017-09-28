from Products.NaayaCore.AuthenticationTool.interfaces import IAuthenticationToolPlugin

class plugins_tool(object):
    """ Read the authentication plugins """

    def getPluginsInfo(self):
        """ Return a list of dictionaries containing the information about the
        plugins """

        plugins = []
        site_manager = self.getSite().getSiteManager()
        plugin_classes = site_manager.getAllUtilitiesRegisteredFor(
                    IAuthenticationToolPlugin)

        for klass in plugin_classes:
            plugins.append({
                'name': klass.__name__,
                'doc': klass.__doc__,
                'object_type': klass.object_type
            })
        return plugins

    def getPluginFactory(self, object_type):
        """ Return a plugin class based on it's object_type """

        site_manager = self.getSite().getSiteManager()
        for plugin in self.getPluginsInfo():
            if plugin['object_type'] == object_type:
                return site_manager.queryUtility(IAuthenticationToolPlugin,
                                                 plugin['name'])
        return None

    def getKnownMetaTypes(self):
        """ Return a list of known meta_types.

        These meta_types are then used to match with the auth tools in the
        portal.

        """

        return [plugin['object_type'] for plugin in self.getPluginsInfo()]
