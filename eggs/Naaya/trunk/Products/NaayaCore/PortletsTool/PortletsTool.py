"""
This is the container for portlets (sections in a page), Ref trees,
lists of links (used for menus) and others.

"""
from md5 import new as new_md5
import simplejson as json
from copy import copy

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from zope import component
from ZPublisher import NotFound
from App.ImageFile import ImageFile

from Products.NaayaCore.constants import *
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.managers.utils import utils
from managers.portlets_templates import *
from Portlet import manage_addPortlet_html, addPortlet
from HTMLPortlet import manage_addHTMLPortlet_html, addHTMLPortlet
from LinksList import manage_addLinksListForm, manage_addLinksList
from RefList import manage_addRefListForm, manage_addRefList
from RefTree import manage_addRefTreeForm, manage_addRefTree
from naaya.core.zope2util import folder_manage_main_plus
from naaya.core.utils import force_to_unicode

from interfaces import INyPortlet

portlet_template_names = {
    'left': 'portlet_left_macro',
    'right': 'portlet_right_macro',
    'center': 'portlet_center_macro',
}
portlet_template_reverse_names = dict((v,k) for k,v in portlet_template_names.items())


def manage_addPortletsTool(self, REQUEST=None):
    """ """
    ob = PortletsTool(ID_PORTLETSTOOL, TITLE_PORTLETSTOOL)
    self._setObject(ID_PORTLETSTOOL, ob)
    self._getOb(ID_PORTLETSTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class PortletsTool(Folder, utils):
    """ """

    meta_type = METATYPE_PORTLETSTOOL
    icon = 'misc_/NaayaCore/PortletsTool.gif'

    manage_options = (
        Folder.manage_options[:1] +
        ({'label': 'Layout', 'action': 'manage_layout'},) +
        Folder.manage_options[2:]
    )

    security = ClassSecurityInfo()

    meta_types = (
        {'name': METATYPE_PORTLET, 'action': 'manage_addPortlet_html', 'permission': PERMISSION_ADD_NAAYACORE_TOOL},
        {'name': METATYPE_HTMLPORTLET, 'action': 'manage_addHTMLPortlet_html', 'permission': PERMISSION_ADD_NAAYACORE_TOOL},
        {'name': METATYPE_LINKSLIST, 'action': 'manage_addLinksListForm', 'permission': PERMISSION_ADD_NAAYACORE_TOOL},
        {'name': METATYPE_REFLIST, 'action': 'manage_addRefListForm', 'permission': PERMISSION_ADD_NAAYACORE_TOOL},
        {'name': METATYPE_REFTREE, 'action': 'manage_addRefTreeForm', 'permission': PERMISSION_ADD_NAAYACORE_TOOL},
    )
    all_meta_types = meta_types

    #constructors
    manage_addPortlet_html = manage_addPortlet_html
    addPortlet = addPortlet
    manage_addHTMLPortlet_html = manage_addHTMLPortlet_html
    addHTMLPortlet = addHTMLPortlet
    manage_addLinksListForm = manage_addLinksListForm
    manage_addLinksList = manage_addLinksList
    manage_addRefListForm = manage_addRefListForm
    manage_addRefList = manage_addRefList
    manage_addRefTreeForm = manage_addRefTreeForm
    manage_addRefTree = manage_addRefTree

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self._portlet_layout = {}

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

    #api
    def getPortletsTypes(self): return PORTLETS_TYPES
    def getPortlets(self): return self.objectValues([METATYPE_PORTLET, METATYPE_HTMLPORTLET])
    def getLinksLists(self): return self.objectValues(METATYPE_LINKSLIST)
    def getRefLists(self): return self.objectValues(METATYPE_REFLIST)
    def getRefTrees(self): return self.objectValues(METATYPE_REFTREE)
    def getPortletsIds(self): return self.objectIds([METATYPE_PORTLET, METATYPE_HTMLPORTLET])

    def get_html_portlets(self):
        return [x for x in self.objectValues(METATYPE_HTMLPORTLET) if x.portlettype==0]
    def get_linkslists_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==1]
    def get_remotechannels_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==2]
    def get_remotechannelsfacade_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==6]
    def get_localchannels_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype in (3,5)]
    def get_folders_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==4]
    def get_special_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==100]


    #JsTree listing

    security.declareProtected(view, 'get_reftrees_as_json_data')
    def get_reftrees_as_json_data(self):
        """ returns all reftrees (NOT translated) """
        def get_info(node, rel='node'):
            ob = node['ob']
            return {
                'data': ob.title_or_id(),
                'attributes': {
                    'id': ob.getId(),
                    'rel': rel,
                },
                'children': [get_info(kid) for kid in node['children']],
            }

        portal = self.getSite()
        return json.dumps({
            'data': portal.title_or_id(),
            'attributes': {
                'id': portal.getId(),
                'rel': 'root',
            },
            'children': [ get_info(t.get_nodes_as_tree(), rel='tree')
                          for t in self.getRefTrees() ],
        })

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'handle_jstree_actions')
    def handle_jstree_actions(self, data):
        """ """
        data = json.loads(data)
        action = data['action']
        type = data['type']
        if action == 'add':
            if type == 'tree':
                return manage_addRefTree(self, title=data['name'])
            if type == 'node':
                parent_tree = data['parent_tree']['id']
                parent_node = None
                if data['parent']['type'] == 'node':
                    parent_node = data['parent']['id'] or None
                return self[parent_tree].manage_addRefTreeNode(
                    title=data['name'],
                    parent=parent_node,
                    pickable=True)
        elif action == 'rename':
            if data['object_creation']:
                if type == 'tree':
                    obj = self[data['id']]
                    obj_data = {
                        'title': data['new_name'],
                        'description': obj.description,
                        }
                    self.manage_delObjects([data['id']])
                    return manage_addRefTree(self, **obj_data)
                if type == 'node':
                    obj_container = self[data['parent_tree']['id']]
                    obj = obj_container[data['id']]
                    obj_data = {
                        'title': data['new_name'],
                        'pickable': True,
                        'parent': obj.parent,
                    }
                    obj_container.manage_delObjects(data['id'])
                    return obj_container.manage_addRefTreeNode(**obj_data)
            else:
                if type == 'tree':
                    self[data['id']].title = data['new_name']
                if type == 'node':
                    self[data['parent_tree']['id']][data['id']].title = data['new_name']
        elif action == 'delete':
            if type == 'tree':
                self.manage_delObjects(data['id'])
            elif type == 'node':
                to_delete = copy(data['children'])
                to_delete.append(data['id'])
                self[data['parent_tree']['id']].manage_delObjects(to_delete)
        elif action == 'move':
            if type == 'node':
                old_parent_tree = data['old_parent_tree']['id']
                new_parent_tree = data['new_parent_tree']['id']
                new_parent_node = None
                if data['new_parent']['type'] == 'node':
                    new_parent_node = data['new_parent']['id'] or None
                to_cut = copy(data['children'])
                to_cut.append(data['id'])
                cut_data = self[old_parent_tree].manage_cutObjects(to_cut)
                self[new_parent_tree].manage_pasteObjects(cut_data)
                self[new_parent_tree][data['id']].parent = new_parent_node

                if data['new_parent']['type'] == 'tree':
                    parent = None
                else:
                    parent = data['new_parent']['id']
                if data['new_prev'] == data['new_parent']['id']:# First item
                    self[new_parent_tree].move(self[new_parent_tree][data['id']], parent, before=data.get('new_next', None))
                elif 'new_next' in data: # Any item
                    self[new_parent_tree].move(self[new_parent_tree][data['id']], parent, before=data.get('new_next', None))
                else:# Last item
                    self[new_parent_tree].move(self[new_parent_tree][data['id']], parent)
                return data['id']
    def getPortletById(self, p_id):
        """
        Get the portlet with the given id. Returns the portlet from
        ``portal_portlets`` if it exists; otherwise, performs an adapter query
        and returns the result. If no portlet is found, returns ``None``.
        """
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type not in [METATYPE_PORTLET, METATYPE_HTMLPORTLET]: ob = None
        if ob is None:
            ob = component.queryAdapter(self.getSite(), INyPortlet, name=p_id)
            if ob is not None:
                return LegacyPortletWrapper(ob, p_id)
        return ob

    def getPortletMacro(self, p_id, macro):
        """Get the portlet by a given id an return a macro defined from that
        portlet

        """
        portlet = self.getPortletById(p_id)
        if isinstance(portlet, LegacyPortletWrapper):
            return portlet.portlet.template.macros.get(macro, None)
        else:
            return portlet.macros.get(macro, None)

    def getLinksListById(self, p_id):
        #return the links list with the given id
        if not p_id:
            ob = None
        else:
            try:
                ob = self._getOb(p_id)
            except AttributeError:
                raise NotFound('links group %s' % (p_id,))
            if ob.meta_type != METATYPE_LINKSLIST:
                ob = None
        return ob

    def getRefListById(self, p_id):
        #return the selection list with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_REFLIST: ob = None
        return ob

    def getRefTreeById(self, p_id):
        #return the selection tree with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_REFTREE: ob = None
        return ob

    #portlet layout
    def assign_portlet(self, folder_path, position, portlet_id, inherit=True):
        self.__dict__.setdefault('_portlet_layout', {})

        key = (folder_path, position)
        lst = self._portlet_layout.setdefault(key, [])

        for item in lst:
            if item['id'] == portlet_id:
                raise ValueError('Portlet "%s" already assigned to "%s" at "%s"'
                    % (portlet_id, position, folder_path))

        lst.append({'id': portlet_id, 'inherit': inherit})
        self._p_changed = 1

    def unassign_portlet(self, folder_path, position, portlet_id):
        self.__dict__.setdefault('_portlet_layout', {})
        key = (folder_path, position)
        try:
            l = self._portlet_layout[key]
            for i in l:
                if i['id'] == portlet_id:
                    l.remove(i)
                    self._p_changed = 1
                    break
            else:
                raise KeyError
        except KeyError, e:
            raise ValueError('No portlet named "%s" among "%s" portlets at "%s"'
                % (portlet_id, position, folder_path))

    def get_portlet_ids_for(self, folder_path, position):
        if '_portlet_layout' not in self.__dict__:
            return []

        output = []
        if folder_path:
            path_pieces = [''] + (folder_path).split('/')
        else:
            path_pieces = ['']
        paths = ['/'.join(path_pieces[1:c+1]) for c in range(len(path_pieces))]

        for path in paths:
            key = (path, position)
            for portlet in self._portlet_layout.get(key, []):
                if portlet['inherit'] or path is paths[-1]:
                    output.append(portlet['id'])

        return output

    def get_portlets_for_obj(self, obj, position):
        """
        Returns a list with all portlets that should be displayed on the index
        page of `obj` in the specified position (left, center, right).
        """
        here_location = obj.getPhysicalPath()
        site_location = self.getSite().getPhysicalPath()
        folder_path = '/'.join(here_location[len(site_location):])
        portlet_ids = self.get_portlet_ids_for(folder_path, position)

        # begin backwards compatibility code
        old_data = lambda name: self.getSite().__dict__['_portlets_manager__%s' % name]
        old_ids = []
        if position == 'center':
            if obj is self.getSite():
                old_ids.extend(old_data('center_portlets_ids'))
        elif position == 'left':
            old_ids.extend(old_data('left_portlets_ids'))
        elif position == 'right':
            if obj is self.getSite():
                old_ids.extend(old_data('right_portlets_locations').get('', []))
            else:
                old_dict = old_data('right_portlets_locations')
                for p in self.getSite().getAllParents(obj):
                    old_ids.extend(old_dict.get(p.absolute_url(1), []))
        portlet_ids = old_ids + portlet_ids
        # end backwards compatibility code

        return list(self._get_portlets_for_ids(portlet_ids))

    def _get_portlets_for_ids(self, portlet_ids):
        for portlets_id in portlet_ids:
            portlet = self.getPortletById(portlets_id)
            if portlet is not None:
                yield portlet

    #administration
    def index_html(self, REQUEST):
        """ redirect to admin_layout """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_layout')

    def _process_layout_post(self, REQUEST):
        form = REQUEST.form
        action = form.get('action', None)

        if action == 'Assign':
            portlet_id = form['portlet_id']
            portlet = self.getPortletById(portlet_id)
            location = form['location']
            position = form['position']
            inherit = form.get('inherit', False)
            site_base_url = self.getSite().absolute_url(1)
            if site_base_url and location.startswith(site_base_url):
                location = location[len(site_base_url)+1:]
            if location == '/':
                location = ''
            try:
                self.assign_portlet(location, position, portlet_id, inherit)
            except ValueError, e:
                if 'already assigned' in str(e):
                    self.setSessionErrorsTrans('Portlet "${title}" already assigned to "${position}" at "${location}"',
                        title=portlet.title_or_id(), position=position, location=(location or "[site root]"))
                else:
                    raise
            else:
                self.setSessionInfoTrans('Successfully assigned portlet "${title}" at "${location}"',
                    title=portlet.title_or_id(), location=(location or "[site root]"))

        elif action == 'Unassign':
            portlet_id = form['portlet_id']
            portlet = self.getPortletById(portlet_id)
            location = form['location']
            position = form['position']
            self.unassign_portlet(location, position, portlet_id)
            self.setSessionInfoTrans('Successfully removed portlet "${title}" from "${location}"',
                title=portlet.title_or_id(), location=(location or "[site root]"))

        elif action == 'ToggleInherit':
            portlet_id = form['portlet_id']
            portlet = self.getPortletById(portlet_id)
            location = form['location']
            key = (location, form['position'])
            for i in self._portlet_layout[key]:
                if i['id'] == portlet_id:
                    inherit = i['inherit'] = not i['inherit']
                    self._p_changed = True
                    self.setSessionInfoTrans('Successfully changed portlet inheritance "${title}" at "${location}" to ${inherit}',
                        title=portlet.title_or_id(), location=(location or "[site root]"),
                        inherit=inherit
                    )
                    break

        else:
            raise ValueError('Unknown value for `action`: %s' % repr(action))

    _admin_layout_zpt = NaayaPageTemplateFile('zpt/admin_layout', globals(),
        'portlets_tool_admin_layout')
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_layout')
    def admin_layout(self, REQUEST):
        """ Administration page for portlets layout """
        if REQUEST.REQUEST_METHOD == 'POST':
            self._process_layout_post(REQUEST)
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_layout')

        options = {
            'portlet_layout': ordered_portlets(self._enumerate_portlet_assignments()),
        }
        return self._admin_layout_zpt(REQUEST, **options)

    _manage_layout_zpt = PageTemplateFile('zpt/manage_layout', globals())
    security.declareProtected(view_management_screens, 'manage_layout')
    def manage_layout(self, REQUEST=None):
        """ ZMI page for portlets layout """
        if REQUEST.REQUEST_METHOD == 'POST':
            self._process_layout_post(REQUEST)
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_layout')

        options = {
            'portlet_layout': ordered_portlets(self._enumerate_portlet_assignments()),
            'admin_layout_zpt': self._admin_layout_zpt,
        }
        return self._manage_layout_zpt(REQUEST, **options)

    def _enumerate_portlet_assignments(self):
        """ Enumerate portlet assignments in this portal """
        assignments = dict()

        def add_portlet_if_exists(portlet_id, folder_path, position, inherit, oldstyle=False):
            portlet = self.getPortletById(portlet_id)
            if portlet is not None:
                key = (folder_path, position)
                data = {
                    'portlet': portlet,
                    'folder_path': folder_path,
                    'position': position,
                    'inherit': inherit,
                }
                data['hashkey'] = simplehash(data)
                data['oldstyle'] = oldstyle
                assignments.setdefault(key, list()).append(data)

        old_data = lambda name: self.getSite().__dict__['_portlets_manager__%s' % name]

        for portlet_id in old_data('center_portlets_ids'):
            add_portlet_if_exists(portlet_id, '', 'center', False, oldstyle=True)

        for portlet_id in old_data('left_portlets_ids'):
            add_portlet_if_exists(portlet_id, '', 'left', True, oldstyle=True)

        for location, portlet_ids in old_data('right_portlets_locations').iteritems():
            for portlet_id in portlet_ids:
                add_portlet_if_exists(portlet_id, location, 'right', True, oldstyle=True)

        _portlet_layout = getattr(self, '_portlet_layout', {})
        for key in sorted(_portlet_layout.iterkeys(), key=lambda i: (i[1],i[0])):
            for portlet_data in _portlet_layout[key]:
                add_portlet_if_exists(portlet_data['id'], key[0], key[1],
                    portlet_data['inherit'])

        return assignments

    def get_all_portlets(self):
        output = []
        names = set()
        for portlet_id in self.getPortletsIds():
            output.append(self.getPortletById(portlet_id))
            names.add(portlet_id)

        site = self.getSite()
        for portlet_id, portlet in component.getAdapters((site,), INyPortlet):
            if portlet_id not in names:
                output.append(LegacyPortletWrapper(portlet, portlet_id))
                names.add(portlet_id)

        output.sort(key=lambda portlet: force_to_unicode(portlet.title_or_id().lower()))
        return output

    def sort_portlets(self, REQUEST, portlet_order):
        """ Ajax method that changes order of portlets in a group """
        if isinstance(portlet_order, basestring):
            portlet_order = [portlet_order]
        all_assignments = self._enumerate_portlet_assignments()

        _portlet_layout = getattr(self, '_portlet_layout', {})
        for key, assignments in all_assignments.iteritems():
            entry_by_hash = dict((entry['hashkey'], entry)
                                 for entry in assignments)
            ordered_entries = []
            for hashkey in portlet_order:
                if hashkey in entry_by_hash:
                    ordered_entries.append(entry_by_hash.pop(hashkey))
            ordered_entries += entry_by_hash.values()
            _portlet_layout[key] = [{'id': item['portlet'].id,
                                     'inherit': item['inherit']}
                                    for item in ordered_entries]

        self._p_changed = True

        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def _get_macro(self, name):
        tmpl_name = portlet_template_names[name]
        skin = self.getSite().getLayoutTool().getCurrentSkin()
        return skin.getTemplateById(tmpl_name).macros['portlet']

    #zmi actions
    security.declareProtected(view_management_screens, 'manage_left_portlets')
    def manage_left_portlets(self, portlets=[], REQUEST=None):
        """ """
        self.getSite().set_left_portlets_ids(self.utConvertToList(portlets))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_left_portlets_html')

    security.declareProtected(view_management_screens, 'manage_center_portlets')
    def manage_center_portlets(self, portlets=[], REQUEST=None):
        """ """
        self.getSite().set_center_portlets_ids(self.utConvertToList(portlets))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_center_portlets_html')

    security.declareProtected(view_management_screens, 'manage_set_right_portlets')
    def manage_set_right_portlets(self, portlets=[], folder='', REQUEST=None):
        """ """
        self.getSite().set_right_portlets_locations(folder, self.utConvertToList(portlets))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_right_portlets_html')

    security.declareProtected(view_management_screens, 'manage_delete_right_portlets')
    def manage_delete_right_portlets(self, ids=[], REQUEST=None):
        """ """
        ids = self.utConvertToList(ids)
        ob = self.getSite()
        for pair in ids:
            location, id = pair.split('||')
            ob.delete_right_portlets_locations(location, id)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_right_portlets_html')

    manage_main = folder_manage_main_plus

    security.declareProtected(view_management_screens, 'ny_after_listing')
    ny_after_listing = PageTemplateFile('zpt/manage_portlets_from_code', globals())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_left_portlets_html')
    manage_left_portlets_html = PageTemplateFile('zpt/manage_left_portlets', globals())

    security.declareProtected(view_management_screens, 'manage_center_portlets_html')
    manage_center_portlets_html = PageTemplateFile('zpt/manage_center_portlets', globals())

    security.declareProtected(view_management_screens, 'manage_right_portlets_html')
    manage_right_portlets_html = PageTemplateFile('zpt/manage_right_portlets', globals())

    jstree_admin_js = ImageFile('www/jstree_admin.js', globals())

InitializeClass(PortletsTool)

class LegacyPortletWrapper(object):
    security = ClassSecurityInfo()

    def __init__(self, portlet, portlet_id):
        self.portlet_id = portlet_id
        self.portlet = portlet

    security.declarePublic('id')
    @property
    def id(self):
        return self.portlet_id

    def getId(self):
        return self.id

    def __call__(self, options):
        position = portlet_template_reverse_names[options['portlet_macro']]
        return self.portlet(options['here'], position)

    def title_or_id(self):
        return self.portlet.title

    def get_type_label(self):
        return 'Special'

    def __repr__(self):
        """
        needed, since it's used when calculating `simplehash` for wrapped
        portlets
        """
        return '<LegacyPortletWrapper for %r>' % self.id

InitializeClass(LegacyPortletWrapper)

def simplehash(data):
    """ generate a hex hashkey for a simple dict """
    h = new_md5()
    for key, value in sorted(data.items()):
        h.update('%s=%s,' % (repr(key), repr(value)))
    return h.hexdigest()

def ordered_portlets(assignments):
    """ sort the portlet assignments by path """
    position_names = ('left', 'right', 'center')
    positions = dict( (name, dict()) for name in position_names )
    for key, value in assignments.iteritems():
        location, position = key
        positions[position][location] = value
    output = []
    for name in position_names:
        position = positions[name]
        for location in sorted(position.iterkeys()):
            output.append( (name, position[location]) )
    return output
