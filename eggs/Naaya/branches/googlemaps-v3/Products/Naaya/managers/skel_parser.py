import os.path
import logging
from xml.dom import minidom


log = logging.getLogger(__name__)


# Translation Map
'''
Key is path in xml, starting from root (<skel> tag)
Dict specifies new name (optional) and type of element: `node`, `list` or `dict`
Used for handling attribute type in skel tree and for returning
default values (None, [] or {}) in __getattr__

'''
TAG_MAPPING = {
    'forms/form': {'rename': 'forms', 'type': 'list'},
    'security/role': {'rename': 'roles', 'type': 'list'},
    'security/role/permission': {'rename': 'permissions', 'type': 'list'},
    'pluggablecontenttypes/pluggablecontenttype': {
        'rename': 'pluggablecontenttypes', 'type': 'list'},
    'properties/language': {'rename': 'languages', 'type': 'list'},
    'layout/skin': {'rename': 'skins', 'type': 'list'},
    'layout/skin/file': {'rename': 'files', 'type': 'list'},
    'layout/skin/template': {'rename': 'templates', 'type': 'list'},
    'layout/skin/style': {'rename': 'styles', 'type': 'list'},
    'layout/skin/image': {'rename': 'images', 'type': 'list'},
    'layout/skin/scheme': {'rename': 'schemes', 'type': 'list'},
    'layout/skin/diskfile': {'rename': 'diskfiles', 'type': 'list'},
    'layout/skin/disktemplate': {'rename': 'disktemplates', 'type': 'list'},
    'layout/skin/folder': {'rename': 'folders', 'type': 'list'},
    'layout/skin/folder/diskfile': {'rename': 'diskfiles', 'type': 'list'},
    'layout/skin/folder/file': {'rename': 'files', 'type': 'list'},
    'layout/skin/scheme/style': {'rename': 'styles', 'type': 'list'},
    'layout/skin/scheme/file': {'rename': 'files', 'type': 'list'},
    'layout/skin/scheme/image': {'rename': 'images', 'type': 'list'},
    'layout/skin/scheme/diskfile': {'rename': 'diskfiles', 'type': 'list'},
    'layout/skin/scheme/disktemplate': {'rename': 'disktemplates',
                                        'type': 'list'},
    'syndication/namespace': {'rename': 'namespaces', 'type': 'list'},
    'syndication/channeltype': {'rename': 'channeltypes', 'type': 'list'},
    'syndication/scriptchannel': {'rename': 'scriptchannels', 'type': 'list'},
    'syndication/localchannel': {'rename': 'localchannels', 'type': 'list'},
    'syndication/remotechannel': {'rename': 'remotechannels', 'type': 'list'},
    'portlets/portlet': {'rename': 'portlets', 'type': 'list'},
    'portlets/assign': {'type': 'list'},
    'portlets/linkslist': {'rename': 'linkslists', 'type': 'list'},
    'portlets/linkslist/link': {'rename': 'links', 'type': 'list'},
    'portlets/reflist': {'rename': 'reflists', 'type': 'list'},
    'portlets/reflist/item': {'rename': 'items', 'type': 'list'},
    'portlets/reftree': {'rename': 'reftrees', 'type': 'list'},
    'portlets/reftree/node': {'rename': 'nodes', 'type': 'list'},
    'portlets/reftree/property': {'rename': 'properties', 'type': 'dict'},
    'emails/emailtemplate': {'rename': 'emailtemplates', 'type': 'list'},
    'map/symbol': {'rename': 'symbols', 'type': 'list'},
}

# create secondary keys for the same dict, based on renamed path
REVERSE_TAG_MAPPING = {}
for k in TAG_MAPPING.keys():
    if TAG_MAPPING[k].has_key('rename'):
        # if it's renamed, construct new mapping
        REVERSE_TAG_MAPPING[k[:k.rfind('/')+1] + TAG_MAPPING[k]['rename']] = TAG_MAPPING[k]
    else:
        REVERSE_TAG_MAPPING[k] = TAG_MAPPING[k]

class SkelTree(object):
    """
    Represents a Node in a SkelTree - it can actually be a leaf,
    the root of the whole tree, or a subtree root.
    The attributes are its children.

    """
    skel_element_path = ()

    def __getitem__(self, key):
        return getattr(self, key)

    def __getattr__(self, name):
        k = '/'.join(self.skel_element_path + (name, ))
        if REVERSE_TAG_MAPPING.has_key(k):
            spec = REVERSE_TAG_MAPPING[k]
            if spec['type'] == 'list':
                return []
            elif spec['type'] == 'node':
                return None
            elif spec['type'] == 'dict':
                return {}
            else:
                raise ValueError('unexpected value: spec[\'type\'] = %r' % spec['type'])
        else:
            return None

class skel_parser(object):
    """ Class that handles parsing of skeleton xml """

    def build_tree(self, node, tag_path=()):
        """
        Build a tree recursively.
         * `node`: the current node of xml dom
         * `tag_path`: list containing parents' name
           of current node of xml dom (path)

        """
        name = str(node.nodeName)
        new = SkelTree()
        new.skel_element_path = tag_path
        attrs = dict(node.attributes)
        for attribute in attrs.keys():
            # attribute value must be ascii!
            attr_value = attrs[attribute].value.encode("ascii")
            setattr(new, attribute, attr_value)

        for c in node.childNodes:
            if (c.nodeType != minidom.Node.ELEMENT_NODE):
                continue
            path = tag_path + (c.nodeName, )
            name = c.nodeName
            if TAG_MAPPING.has_key('/'.join(path)):
            # we have a hardcoded specification for this path
                spec = TAG_MAPPING['/'.join(path)]
                if spec.has_key('rename'):
                    name = spec['rename']
                if spec['type'] == 'list':
                    # element is part of a list of nodes
                    current = getattr(new, name, [])
                    if current:
                        current.append(self.build_tree(c, path))
                    else:
                        # first occurrence
                        setattr(new, name, [self.build_tree(c, path)])
                    continue
                elif spec['type'] == 'node':
                    # default behavior for connecting child
                    pass
            setattr(new, name, self.build_tree(c, path))

        return new

    def parse(self, p_content):
        """ """
        try:
            dom = minidom.parseString(p_content).childNodes[0]
        except Exception, error:
            return (None, error)
        # initializations
        skel_handler = SkelTree()
        skel_handler.root = self.build_tree(dom)
        return (skel_handler, '')


def skel_handler_for_path(skel_path):
    f = open(os.path.join(skel_path, 'skel.xml'), 'rb')
    skel_content = f.read()
    f.close()
    skel_handler, error = skel_parser().parse(skel_content)
    if error:
        log.error(error)
        raise ValueError('error parsing skel.xml')

    skel_handler.skel_path = skel_path
    return skel_handler
