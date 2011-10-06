import simplejson as json

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import *
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
from RefTreeNode import manage_addRefTreeNodeForm, manage_addRefTreeNode, \
                        localizer_patcher
from Products.NaayaCore.managers.utils import make_id

manage_addRefTreeForm = PageTemplateFile('zpt/reftree_manage_add', globals())
def manage_addRefTree(self, id='', title='', description='', lang=None,
                      REQUEST=None):
    """ """
    id = make_id(self, id=id, title=title, prefix=PREFIX_SUFIX_REFTREE)
    if lang is None: lang = self.gl_get_selected_language()
    ob = RefTree(id, title, description, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return id


class RefTree(LocalPropertyManager, Folder):
    """ """

    meta_type = METATYPE_REFTREE
    icon = 'misc_/NaayaCore/RefTree.gif'

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    security = ClassSecurityInfo()

    meta_types = ({
        'name': METATYPE_REFTREENODE,
        'action': 'manage_addRefTreeNodeForm',
        'permission': PERMISSION_ADD_NAAYACORE_TOOL
    },)
    all_meta_types = meta_types

    title = localizer_patcher

    #constructors
    manage_addRefTreeNodeForm = manage_addRefTreeNodeForm
    manage_addRefTreeNode = manage_addRefTreeNode

    def __init__(self, id, title, description, lang):
        """ """
        self.id = id
        self.title = title
        self.description = description

    def _setObject(self, object_id, object, set_owner = 0):
        """
        Reorder B{object}'s level by weight
        Each time a new node is appended to the tree the level it wants to seat
        on will be reorded by weight (easy objects float, heavy objects sink)
        """
        node_siblings = self.get_node_children(object.parent)
        weight = 0
        for node in node_siblings: # Reordering
            node.weight = weight
            weight += 1
        object.weight = weight # Put this node at the last position
        super(RefTree, self)._setObject(object_id, object, set_owner)

    def move(self, ob, parent=None, after=None, before=None):
        """ Moves ob"""
        if after and before:
            raise ValueError('Provide just one argument \'after\' or \'before\''
                             'not both')
        node_siblings = self.get_node_children(parent)# Get new parent's children
        if not after and not before: # Move to parent
            if ob.parent != parent: # Parent changed move node
                if parent and self.is_child(ob.getId(), parent):#Check if parent is not child of ob
                    raise ValueError('Illegal move operation')
                # Check if operation is legal
                ob.parent = parent
                weight = 0
                for node in node_siblings: # Reordering
                    weight += 1
                ob.weight = weight # Last item
        elif after and not before:
            for node in node_siblings:# After
                if node.id == after:
                    if parent and self.is_child(ob.getId(), parent): # Check if parent is not child of ob
                        raise ValueError('Illegal move operation')
                    ob.parent = parent
                    weight = 0
                    for rnode in node_siblings: # Reordering
                        rnode.weight = weight
                        if rnode.id == after:
                            ob.weight = rnode.weight + 1
                            weight += 1
                        weight += 1
                    break
        else:
            # Before
            for node in node_siblings:
                if node.id == before:
                    if parent and self.is_child(ob.getId(), parent): # Check if parent is not child of ob
                        raise ValueError('Illegal move operation')
                    ob.parent = parent
                    weight = 0
                    for rnode in node_siblings: # Reordering
                        if rnode.id != ob.id:
                            if rnode.id == before:
                                if rnode.weight == 0:
                                    ob.weight = 0
                                else:
                                    ob.weight = rnode.weight - 1
                                weight += 1
                            rnode.weight = weight
                            weight += 1
                    break

    def is_child(self, parent, ob_id):
        """ Check if ``ob`` is child of ``parent`` recursively"""
        def recurse(ob):
            if ob.parent == parent:
                return True
            elif ob.parent is not None:
                return recurse(self[ob.parent])
            return False
        return recurse(self[ob_id])

    #api
    def get_tree_object(self): return self #What is this?
    def get_tree_path(self, p=0): return self.absolute_url(p) #????
    def get_tree_nodes(self, sort_by='weight'):
        """ Get all tree nodes """
        return self.utSortObjsListByAttr(
            self.objectValues(METATYPE_REFTREENODE), sort_by, 0)

    def get_node_children(self, parent = None, sort_by='weight'):
        """ return child nodes for parent ordered by weight """
        return self.utSortObjsListByAttr([x for x in self.get_tree_nodes()
                                          if parent == x.parent ], sort_by, 0)

    def get_tree(self):
        """ Get tree as a list of dictionaries ordered by weight """
        nodes = self.get_tree_nodes()
        data = []
        visited = []
        def recurse(node):
            if node.id not in visited:
                if node.parent == None or node.parent in visited:
                    visited.append(node.id)
                    ret_dict = {}
                    ret_dict[node] = []
                    if hasattr(node, 'children'):
                        ret_dict[node] = map(recurse, self.get_node_children(node.id))
                    return ret_dict

        for node in nodes:
            res = recurse(node)
            if res:
                data.append(res)

        return data

    security.declareProtected(view, 'get_tree_thread')
    def get_tree_thread(self):
        """ Construct a flattened representation of this tree.  """
        nodes = []

        def add_node(node, depth):
            nodes.append({'depth': depth, 'ob': node['ob']})
            for child_node in node['children']:
                add_node(child_node, depth+1)

        for top_node in self.get_nodes_as_tree()['children']:
            add_node(top_node, 0)

        return nodes


    security.declareProtected(view, 'get_tree_json_data')
    def get_tree_json_data(self):
        """ returns tree data (titles are translated) """
        gettext = self.getSite().getPortalTranslations()

        def get_info(node):
            ob = node['ob']
            return {
                'data': gettext(ob.title_or_id()),
                'attributes': {
                    'id': ob.getId(), # TODO: rename for this field, "id"
                                      # happens to mean someting in HTML.
                    'rel': 'node',
                    'weight': getattr(ob, 'weight', 0),
                },
                'children': [get_info(kid) for kid in node['children']],
            }

        top_nodes = self.get_nodes_as_tree()['children']
        return json.dumps([get_info(node) for node in top_nodes])

    def get_list(self):
        return self.get_tree_nodes()

    def get_leafs(self):
        return [x for x in self.get_tree_nodes() if x.parent == self.getId()]

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', lang=None, REQUEST=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        self.title = title
        self.description = description
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_edit_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/reftree_manage_edit', globals())

    security.declareProtected(view, 'get_nodes_as_tree')
    def get_nodes_as_tree(self):
        node_obs = self.objectValues([METATYPE_REFTREENODE])

        # pass one: create the output objects
        # None represents the root node (the reftree itself)
        out_nodes = {None: {'ob': self, 'children': []}}
        for ob in node_obs:
            out_nodes[ob.getId()] = {'ob': ob, 'children': []}

        # pass two: link them in a tree structure
        top_nodes = []
        for ob in node_obs:
            out_nodes[ob.parent]['children'].append(out_nodes[ob.getId()])

        # pass three: sort the nodes on each branch
        get_weight = lambda n: getattr(n['ob'], 'weight', None)
        for node in out_nodes.itervalues():
            node['children'].sort(key=get_weight)

        return out_nodes[None]

InitializeClass(RefTree)
