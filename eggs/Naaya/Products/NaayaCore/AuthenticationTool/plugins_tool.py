from os.path import join
from os import listdir


from Products.NaayaCore.constants import *

class plugins_tool:
    """ """

    def __init__(self):
        """ """
        self.__plugins = []
        self.loadPlugins()

    def loadPlugins(self):
        #scans the plugins folder and loads information about available sources plugins
        self.__plugins = []
        for l_file in listdir(join(NAAYACORE_PRODUCT_PATH, 'AuthenticationTool', 'plugins')):
            if l_file.startswith('plug') and l_file.endswith('.py'):
                l_file = l_file.replace('.py', '')
                exec('from plugins import %s' % l_file)
                name = eval('%s.plug_name' % l_file)
                doc = eval('%s.plug_doc' % l_file)
                version = eval('%s.plug_version' % l_file)
                object_type = eval('%s.plug_object_type' % l_file)
                self.__plugins.append({'name': name, 'doc': doc, 'version': version, 'object_type': object_type})
        self._p_changed = 1

    def getPlugins(self):
        return self.__plugins

    def getPluginName(self, p_plugin):
        return p_plugin['name']

    def getPluginDoc(self, p_plugin):
        return p_plugin['doc']

    def getPluginVersion(self, p_plugin):
        return p_plugin['version']

    def getPluginObjectType(self, p_plugin):
        return p_plugin['object_type']

    def getPluginInstance(self, p_object_type):
        #given a plugin id returns an instance of that plugin
        plugin_obj = None
        for plugin in self.__plugins:
            if plugin['object_type'] == p_object_type:
                try:
                    exec('from plugins.%s import %s' % (plugin['name'], plugin['name']))
                    plugin_obj = eval('%s()' % plugin['name'])
                except:
                    plugin_obj = None
        return plugin_obj

    def getKnownMetaTypes(self):
        #returns the list of known meta types
        return map(lambda x: x['object_type'], self.__plugins)
