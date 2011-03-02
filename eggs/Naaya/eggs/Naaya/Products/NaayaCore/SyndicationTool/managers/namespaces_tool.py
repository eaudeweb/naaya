
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo


class NamespaceItem:
    """ """

    def __init__(self, id, prefix, value):
        """ """
        self.id = id
        self.prefix = prefix
        self.value = value

    def __str__(self):
        """ """
        if self.prefix=='': 
            return 'xmlns="%s"' % self.value
        else:
            return 'xmlns:%s="%s"' % (self.prefix, self.value)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(NamespaceItem)

class namespaces_tool:
    """ """

    def __init__(self):
        """ """
        self.__namespaces_dictionary = {}

    security = ClassSecurityInfo()

    def __createNamespaceItem(self, id, prefix, value):
        """ """
        obj = NamespaceItem(id, prefix, value)
        self.__namespaces_dictionary[id] = obj

    def __modifyNamespaceItem(self, id, prefix, value):
        """ """
        try: obj = self.__namespaces_dictionary[id]
        except: pass
        else:
            obj.prefix = prefix
            obj.value = value

    def __deleteNamespaceItem(self, id):
        """ """
        try: del(self.__namespaces_dictionary[id])
        except: pass

    def getNamespaceItemsList(self):
        """ """
        try: return self.__namespaces_dictionary.values()
        except: return []

    def getNamespaceItem(self, id):
        """ """
        try: return self.__namespaces_dictionary[id]
        except: return None

    def createNamespaceItem(self, id, prefix, value):
        """ """
        self.__createNamespaceItem(id, prefix, value)
        self._p_changed = 1

    def modifyNamespaceItem(self, id, prefix, value):
        """ """
        self.__modifyNamespaceItem(id, prefix, value)
        self._p_changed = 1

    def deleteNamespaceItem(self, ids):
        """ """
        map(self.__deleteNamespaceItem, ids)
        self._p_changed = 1

    def getNamespaceItemData(self, id):
        """ """
        obj = self.getNamespaceItem(id)
        if obj is not None:
            return ['update',obj.id, obj.prefix, obj.value]
        else:
            return ['add', '', '', '']

InitializeClass(namespaces_tool)
