
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo


class EventType:
    """Defines an Event.
    """

    def __init__(self, p_id, p_title):
        """Init a new object"""
        self.id = p_id
        self.title = p_title

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(EventType)

class events_tool:
    """This class is responsable with event types management.
        All the data is stored in a dictionary like structure:
            - key: event type id
            - value: event type object
    """

    def __init__(self):
        """Constructor"""
        self.__eventtypes = {}

    #security stuff
    security = ClassSecurityInfo()

    def __createEventType(self, p_id, p_title):
        """Add a new object"""
        obj = EventType(p_id, p_title)
        self.__eventtypes[p_id] = obj

    def __modifyEventType(self, p_id, p_title):
        """Modify object"""
        try:
            obj = self.__eventtypes[p_id]
        except:
            pass
        else:
            obj.title = p_title

    def __deleteEventType(self, p_id):
        """Delete an object"""
        try:
            del(self.__eventtypes[p_id])
        except:
            pass

    def getEventTypesList(self):
        """Get a list with all objects"""
        try:
            return self.__eventtypes.values()
        except:
            return []

    def getEventType(self, p_id):
        """Get an object"""
        try:
            return self.__eventtypes[p_id]
        except:
            return None

    def getEventTypeTitle(self, p_id):
        """Get an object title"""
        try:
            return self.__eventtypes[p_id].title
        except:
            return ''

    def createEventType(self, p_id, p_title):
        """Create a new object"""
        self.__createEventType(p_id, p_title)
        self._p_changed = 1

    def modifyEventType(self, p_id, p_title):
        """Modify object's properties"""
        self.__modifyEventType(p_id, p_title)
        self._p_changed = 1

    def deleteEventType(self, p_ids):
        """Delete 1 or more objects"""
        for l_id in p_ids:
            self.__deleteEventType(l_id)
        self._p_changed = 1

    def getEventTypeData(self, p_et_id):
        """ """
        l_et = self.getEventType(p_et_id)
        if l_et is not None:
            return ['update', l_et.id, l_et.title]
        else:
            return ['add', '', '']

InitializeClass(events_tool)
