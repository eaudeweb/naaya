from Products.NaayaCore.AuthenticationTool.interfaces import IAuthenticationToolPlugin

class plugins_tool(object):
    """ Read the authentication plugins """

    def getPlugins(self):
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

    def getPluginInstance(self, object_type):
        """Given a plugin instance based on it's object_type.

        After we got the right plugin we will get the utility that has the same
        name as the class"""

        site_manager = self.getSite().getSiteManager()
        for plugin in self.getPlugins():
            if plugin['object_type'] == object_type:
                try:
                    return site_manager.queryUtility(IAuthenticationToolPlugin,
                            plugin['name'])()
                except:
                    self.log_current_error()
                    return None
        return None


    def getKnownMetaTypes(self):
        """ Return a list of known meta_types.

        These meta_types are then used to match with the auth tools in the
        portal.

        """

        return [plugin['object_type'] for plugin in self.getPlugins()]

