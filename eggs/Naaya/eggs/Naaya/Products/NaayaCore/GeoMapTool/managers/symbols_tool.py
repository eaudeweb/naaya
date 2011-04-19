
try:
    from PIL import Image
except ImportError:
    have_pil = False
else:
    have_pil = True
from StringIO import StringIO

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from naaya.core.backport import namedtuple

ImageSize = namedtuple('ImageSize', 'w h')

class symbol_item:
    """ """

    sortorder = 100

    @property
    def image_size(self):
        # temporary, until we're sure all symbol_item objects have the property
        return self._calculate_image_size()

    def __init__(self, id, title, description, parent, picture, sortorder):
        self.id = id
        self.title = title
        self.description = description
        self.parent = parent
        self.setPicture(picture)
        try:
            self.sortorder = int(sortorder)
        except:
            self.sortorder = 100

    def setPicture(self, picture):
        self.picture = None

        if picture not in ('', None):
            if hasattr(picture, 'filename'):
                if picture.filename != '':
                    content = picture.read()
                    if content != '':
                        self.picture = content
            else:
                self.picture = picture

        self.__dict__['image_size'] = self._calculate_image_size()

    def _calculate_image_size(self):
        if not have_pil or self.picture is None:
            return ImageSize(16, 16) # guess a plausible value

        image = Image.open(StringIO(self.picture))
        return ImageSize(*image.size)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(symbol_item)

class symbols_tool:
    """ """

    def __init__(self):
        """ """
        self.__symbol_collection = {}

    def __addSymbol(self, id, title, description, parent, picture, sortorder):
        """ """
        obj = symbol_item(id, title, description, parent, None, sortorder)
        obj.setPicture(picture)
        self.__symbol_collection[id] = obj

    def __updateSymbol(self, id, title, description, parent, picture, sortorder):
        """ """
        try: obj = self.__symbol_collection[id]
        except: pass
        else:
            obj.title = title
            obj.description = description
            obj.parent = parent
            obj.setPicture(picture)
            try:
                obj.sortorder = int(sortorder)
            except:
                obj.sortorder = 100
            obj._p_changed = 1

    def __deleteSymbol(self, id):
        """ """
        try: del(self.__symbol_collection[id])
        except: pass

    def getParentsList(self):
        """Get a list with all parent objects"""
        try: return [ obj for obj in self.__symbol_collection.values() if not obj.parent ]
        except: return []

    def getParentsListOrdered(self):
        """ Get a list with all parent objects ordered by sortorder """
        return self.utSortObjsListByAttr(self.getParentsList(), 'sortorder', 0)

    def getSymbolChildren(self, parent):
        """Get a list with all the children of a parent object"""
        try: return [ obj for obj in self.__symbol_collection.values() if obj.parent == parent ]
        except: return []

    def getSymbolChildrenOrdered(self, parent):
        """Get a list with all the children of a parent object ordered by sortorder """
        return self.utSortObjsListByAttr(self.getSymbolChildren(parent), 'sortorder', 0)

    def getSymbolsList(self):
        """Get a list with all objects"""
        try: return self.__symbol_collection.values()
        except: return []

    def getSymbolsIds(self):
        """Get a list with all objects' ids """
        try: return [x.id for x in self.__symbol_collection.values()]
        except: return []

    def getSymbol(self, id):
        """Get an object"""
        try: return self.__symbol_collection[id]
        except: return None

    def getSymbolData(self, id):
        """ """
        ob = self.getSymbol(id)
        if ob is not None:
            return {'action': 'update', 'id': ob.id, 'title': ob.title,
                'description': ob.description, 'parent': ob.parent, 'picture': ob.picture, 'sortorder': ob.sortorder}
        else:
            return {'action': 'add', 'id': '', 'title': '',
                'description': '', 'parent': '', 'picture': None, 'sortorder': 100}

    def getSymbolTitle(self, id):
        """Get title"""
        try: return self.__symbol_collection[id].title
        except: return id

    def getSymbolParent(self, id):
        """Get parent"""
        try: return self.__symbol_collection[id].parent
        except: return id

    def getSymbolZPicture(self, id, REQUEST=None):
        """Get picture stream in zope interface """
        try:
            return self.__symbol_collection[id].picture
        except: return None

    def getSymbolPicture(self, id, REQUEST=None):
        """Get picture stream"""
        if id.startswith('symbol_cluster'):
            try:
                idx = int(id[len('symbol_cluster_'):])
            except: return None
            try:
                REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
                REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename="%s.jpg"' % id)
                return self._cluster_pngs[idx].index_html(REQUEST, REQUEST.RESPONSE)
            except: return None
        try:
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
            REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename="%s.jpg"' % id)
            return self.__symbol_collection[id].picture
        except: return None

    def updateSymbols(self):
        """ """
        #to be removed
        for id in self.getSymbolsIds():
            if not id.startswith('symbol'):
                obj = self.__symbol_collection[id]
                del self.__symbol_collection[id]
                newobj = symbol_item('symbol%s' % obj.id, obj.title, obj.parent, obj.description, None, obj.sortorder)
                newobj.setPicture(obj.picture)
                self.__symbol_collection['symbol%s' % obj.id] = newobj
        self._p_changed = 1

    def updateSymbolsSortorders(self):
        """ """
        #to be removed
        for id in self.getSymbolsIds():
            obj = self.__symbol_collection[id]
            try:
                obj.sortorder = int(obj.sortorder)
            except:
                obj.sortorder = 100
        self._p_changed = 1

    def updateSymbolsParent(self):
        """ """
        #to be removed
        for id in self.getSymbolsIds():
            obj = self.__symbol_collection[id]
            del self.__symbol_collection[id]
            newobj = symbol_item(obj.id, obj.title, '', obj.description, None, obj.sortorder)
            newobj.setPicture(obj.picture)
            self.__symbol_collection[obj.id] = newobj
        self._p_changed = 1

    def addSymbol(self, id, title, description, parent, picture, sortorder):
        """ """
        self.__addSymbol(id, title, description, parent, picture, sortorder)
        self._p_changed = 1

    def updateSymbol(self, id, title, description, parent, picture, sortorder):
        """ """
        self.__updateSymbol(id, title, description, parent, picture, sortorder)
        self._p_changed = 1

    def deleteSymbol(self, ids):
        """ """
        map(self.__deleteSymbol, ids)
        self._p_changed = 1

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(symbols_tool)

