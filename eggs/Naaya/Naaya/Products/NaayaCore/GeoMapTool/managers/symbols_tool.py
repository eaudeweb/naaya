
from StringIO import StringIO
import re
import PIL.Image
import PIL.ImageDraw


from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from naaya.core.backport import namedtuple

CIRCLE_IMAGE_SIZE = 12

ImageSize = namedtuple('ImageSize', 'w h')

class symbol_item:
    """ """

    sortorder = 100
    color = None

    @property
    def image_size(self):
        # temporary, until we're sure all symbol_item objects have the property
        return self._calculate_image_size()

    def __init__(self, id, title, description, parent, color, picture, sortorder):
        self.id = id
        self.title = title
        self.description = description
        self.parent = parent
        self.setPicture(picture)
        self.color = color
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

        if self.picture is not None:
            self.__dict__['image_size'] = self._calculate_image_size()
        else:
            if 'image_size' in self.__dict__:
                del self.__dict__['image_size']

    def _calculate_image_size(self):
        if self.color is not None:
            return ImageSize(CIRCLE_IMAGE_SIZE, CIRCLE_IMAGE_SIZE)

        if self.picture is None:
            return ImageSize(16, 16) # guess a plausible value

        image = PIL.Image.open(StringIO(self.picture))
        return ImageSize(*image.size)

    def getPicture(self, options={}):
        if self.color is None:
            return self.picture

        else:
            size = int(options.get('size', CIRCLE_IMAGE_SIZE))
            halo = bool(options.get('halo', False))
            return colored_circle(size, self.color, halo)

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(symbol_item)

class symbols_tool:
    """ """

    def __init__(self):
        """ """
        self.__symbol_collection = {}

    def __addSymbol(self, id, title, description, parent, color, picture, sortorder):
        """ """
        if not title:
            raise ValueError('The title is required')

        if color is None and not picture:
            raise ValueError('A color code or an icon is required')

        if color:
            if not check_colorcode(color):
                raise ValueError('Invalid color code: %s' % color)
            if len(color) == 6:
                color = '#' + color
            picture = None

        obj = symbol_item(id, title, description, parent, color, None, sortorder)
        if picture:
            obj.setPicture(picture)
        self.__symbol_collection[id] = obj

    def __updateSymbol(self, id, title, description, parent, color, picture, sortorder):
        """ """

        try: obj = self.__symbol_collection[id]
        except: pass
        else:
            if color is None and not picture and not obj.picture:
                raise ValueError('A color code or an icon is required')

            if color:
                if not check_colorcode(color):
                    raise ValueError('Invalid color code: %s' % color)
                if len(color) == 6:
                    color = '#' + color
                picture = None

            obj.title = title
            obj.description = description

            obj.parent = parent
            if obj.parent:
                for child in self.getSymbolChildren(obj.id):
                    child.parent = ''

            if picture:
                obj.setPicture(picture)
            try:
                obj.sortorder = int(sortorder)
            except:
                obj.sortorder = 100

            obj.color = color
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

    def getParentByTitle(self, title):
        for parent in self.getParentsList():
            if parent.title == title:
                return parent
        raise ValueError(u"Parent not found for this title: %s" % title)

    def getSymbolByTitle(self, title):
        for symbol in self.getSymbolsList():
            if symbol.title == title:
                return symbol
        raise ValueError(u"Symbol not found for this title: %s" % title)

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
            return {
                'action': 'update',
                'id': ob.id,
                'title': ob.title,
                'description': ob.description,
                'parent': ob.parent,
                'color': ob.color,
                'picture': ob.picture,
                'sortorder': ob.sortorder,
            }
        else:
            return {
                'action': 'add',
                'id': '',
                'title': '',
                'description': '',
                'parent': '',
                'color': None,
                'picture': None,
                'sortorder': 100,
            }

    def getSymbolTitle(self, id):
        """Get title"""
        try: return self.__symbol_collection[id].title
        except: return id

    def getSymbolParent(self, id):
        """Get parent"""
        try: return self.__symbol_collection[id].parent
        except: return id

    def getSymbolPicture(self, id='', REQUEST=None):
        """Get picture stream"""
        if id.startswith('symbol_cluster'):
            try:
                idx = int(id[len('symbol_cluster_'):])
            except: return None

            if REQUEST is None:
                return self._cluster_pngs[idx]
            else:
                RESPONSE = REQUEST.RESPONSE
                RESPONSE.setHeader('Content-Type', 'image/jpeg')
                RESPONSE.setHeader('Content-Disposition',
                                   'inline; filename="%s.jpg"' % id)
                return self._cluster_pngs[idx].index_html(REQUEST, RESPONSE)
        else:
            try:
                symbol = self.__symbol_collection[id]
            except: return None

            if REQUEST is None:
                return symbol.getPicture()
            else:
                RESPONSE = REQUEST.RESPONSE
                RESPONSE.setHeader('Content-Type', 'image/jpeg')
                RESPONSE.setHeader('Content-Disposition',
                                   'inline; filename="%s.jpg"' % id)
                return symbol.getPicture(dict(REQUEST.form))

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

    def addSymbol(self, id, title, description, parent, color, picture, sortorder):
        """ """
        self.__addSymbol(id, title, description, parent, color, picture, sortorder)
        self._p_changed = 1

    def updateSymbol(self, id, title, description, parent, color, picture, sortorder):
        """ """
        self.__updateSymbol(id, title, description, parent, color, picture, sortorder)
        self._p_changed = 1

    def deleteSymbol(self, ids):
        """ """
        map(self.__deleteSymbol, ids)
        self._p_changed = 1

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(symbols_tool)


def parse_color(value, _color_pattern=re.compile(
        r'^#(?P<R>[0-9a-f]{2})(?P<G>[0-9a-f]{2})(?P<B>[0-9a-f]{2})$')):
    m = _color_pattern.match(value.lower())
    if m is None:
        raise ValueError("Invalid color spec: %r" % value)
    return (
        int(m.group('R'), 16),
        int(m.group('G'), 16),
        int(m.group('B'), 16),
    )


def check_colorcode(color):
    match_expr = re.compile(r'^#?([a-fA-F0-9]{6})', re.IGNORECASE)
    return re.match(match_expr, color)

def colored_circle(size, color, halo=False):
    image_2x = PIL.Image.new("RGBA", (size*2, size*2), (128, 128, 128, 0))
    draw = PIL.ImageDraw.Draw(image_2x)

    if halo:
        draw.ellipse((1, 1, size*2-2, size*2-2), fill=parse_color('#000000'))
        draw.ellipse((4, 4, size*2-5, size*2-5), fill=parse_color('#ffffff'))
        draw.ellipse((7, 7, size*2-8, size*2-8), fill=parse_color(color))
    else:
        draw.ellipse((1, 1, size*2-2, size*2-2), fill=parse_color(color))

    image = image_2x.resize((size, size), PIL.Image.ANTIALIAS)
    data = StringIO()
    image.save(data, "PNG")
    return data.getvalue()


def handle_skel_event(event):
    site = event.site
    skel_handler = event.skel_handler
    portal_map = site.getGeoMapTool()
    symbols = getattr(skel_handler.root.map, 'symbols', [])
    for symbol in symbols:
        portal_map.addSymbol(symbol.id, symbol.title, symbol.description,
                             symbol.parent, symbol.color, symbol.picture,
                             symbol.sortorder)
