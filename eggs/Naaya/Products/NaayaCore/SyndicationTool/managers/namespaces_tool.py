
from AccessControl.class_init import InitializeClass
from AccessControl import ClassSecurityInfo


class NamespaceItem:
    """ Namespace item """

    def __init__(self, id, prefix, value):
        """ Init """
        self.id = id
        self.prefix = prefix
        self.value = value

    def __str__(self):
        """ Str """
        if self.prefix=='': 
            return 'xmlns="%s"' % self.value
        else:
            return 'xmlns:%s="%s"' % (self.prefix, self.value)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(NamespaceItem)

class namespaces_tool:
    """ Namespaces tool """

    def __init__(self):
        """ Init """
        self.__namespaces_dictionary = {}

    security = ClassSecurityInfo()

    def __createNamespaceItem(self, id, prefix, value):
        """ Create namespace item """
        obj = NamespaceItem(id, prefix, value)
        self.__namespaces_dictionary[id] = obj

    def __modifyNamespaceItem(self, id, prefix, value):
        """ Modify namespace item """
        try: obj = self.__namespaces_dictionary[id]
        except: pass
        else:
            obj.prefix = prefix
            obj.value = value

    def __deleteNamespaceItem(self, id):
        """ Delete namespace item """
        try: del(self.__namespaces_dictionary[id])
        except: pass

    def getNamespaceItemsList(self):
        """ Get namespace items list """
        try: return self.__namespaces_dictionary.values()
        except: return []

    def getNamespaceItem(self, id):
        """ Get namespace item """
        try: return self.__namespaces_dictionary[id]
        except: return None

    def createNamespaceItem(self, id, prefix, value):
        """ Create namespace item """
        self.__createNamespaceItem(id, prefix, value)
        self._p_changed = 1

    def modifyNamespaceItem(self, id, prefix, value):
        """ Modify namespace item """
        self.__modifyNamespaceItem(id, prefix, value)
        self._p_changed = 1

    def deleteNamespaceItem(self, ids):
        """ Delete namespace item """
        for item_id in ids:
            self.__deleteNamespaceItem(item_id)
        self._p_changed = 1

    def getNamespaceItemData(self, id):
        """ Get namespace item data """
        obj = self.getNamespaceItem(id)
        if obj is not None:
            return ['update',obj.id, obj.prefix, obj.value]
        else:
            return ['add', '', '', '']

InitializeClass(namespaces_tool)
