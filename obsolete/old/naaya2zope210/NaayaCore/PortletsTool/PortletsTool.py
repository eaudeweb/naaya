# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web and Finsiel Romania
# are Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
# Alex Morega, Eau de Web

#Python imports
from md5 import new as new_md5

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from managers.portlets_templates import *
from Portlet import manage_addPortlet_html, addPortlet
from HTMLPortlet import manage_addHTMLPortlet_html, addHTMLPortlet
from LinksList import manage_addLinksListForm, manage_addLinksList
from RefList import manage_addRefListForm, manage_addRefList
from RefTree import manage_addRefTreeForm, manage_addRefTree

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
        Folder.manage_options[:1]
        +
        (
            {'label': 'Left portlets', 'action': 'manage_left_portlets_html'},
            {'label': 'Center portlets', 'action': 'manage_center_portlets_html'},
            {'label': 'Right portlets', 'action': 'manage_right_portlets_html'},
        )
        +
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
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==3]
    def get_folders_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==4]
    def get_special_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==100]

    def getPortletById(self, p_id):
        #return the portlet with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type not in [METATYPE_PORTLET, METATYPE_HTMLPORTLET]: ob = None
        return ob

    def getLinksListById(self, p_id):
        #return the links list with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_LINKSLIST: ob = None
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
            portlet = self._getOb(portlets_id, None)
            if portlet is not None:
                yield portlet

    #administration
    def index_html(self, REQUEST):
        """ redirect to admin_layout """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_layout')

    _admin_layout_zpt = PageTemplateFile('zpt/admin_layout', globals())
    security.declareProtected(view_management_screens, 'admin_layout')
    def admin_layout(self, REQUEST):
        """ Administration page for portlets layout """
        if REQUEST.REQUEST_METHOD == 'POST':
            form = REQUEST.form
            action = form.get('action', None)
            if action == 'Assign':
                portlet_id = form['portlet_id']
                portlet = self._getOb(portlet_id)
                location = form['location']
                position = form['position']
                inherit = form.get('inherit', False)
                site_base_url = self.getSite().absolute_url(1)
                if site_base_url and location.startswith(site_base_url):
                    location = location[len(site_base_url)+1:]
                if location == '__root':
                    location = ''
                try:
                    self.assign_portlet(location, position, portlet_id, inherit)
                except ValueError, e:
                    if 'already assigned' in str(e):
                        self.setSessionErrors(['Portlet "%s" already assigned to '
                            '"%s" at "%s"' % (portlet.title_or_id(), position, location)])
                    else:
                        raise
                else:
                    self.setSessionInfo(['Successfully assigned portlet "%s" at "%s"'
                        % (portlet.title_or_id(), location)])

            elif action == 'Unassign':
                portlet_id = form['portlet_id']
                portlet = self._getOb(portlet_id)
                location = form['location']
                position = form['position']
                self.unassign_portlet(location, position, portlet_id)
                self.setSessionInfo(['Successfully removed portlet "%s" from "%s"'
                    % (portlet.title_or_id(), location)])

            else:
                raise ValueError('Unknown value for `action`: %s' % repr(action))

        return self._admin_layout_zpt(REQUEST,
            portlet_layout=ordered_portlets(self._enumerate_portlet_assignments()))

    def _enumerate_portlet_assignments(self):
        """ Enumerate portlet assignments in this portal """
        assignments = dict()

        def add_portlet_if_exists(portlet_id, folder_path, position, inherit, oldstyle=False):
            portlet = self._getOb(portlet_id, None)
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
        for portlet_id in self.getPortletsIds():
            output.append(self._getOb(portlet_id))
        return output

    def sort_portlets(self, REQUEST, folder_path, position, portlet_order):
        """ Ajax method that changes order of portlets in a group """
        if isinstance(portlet_order, basestring):
            portlet_order = [portlet_order]
        assignments = self._enumerate_portlet_assignments()
        key = (folder_path, position)
        by_hash = dict( (entry['hashkey'], entry) for entry in assignments[key])

        if set(by_hash.keys()) != set(portlet_order):
            raise ValueError('Not the same portlets')

        _portlet_layout = getattr(self, '_portlet_layout', {})
        _portlet_layout[key] = [{'id': item['portlet'].id, 'inherit': item['inherit']}
                                for item in (by_hash[h] for h in portlet_order)]
        self._p_changed = True

        return 'ok'

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

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_left_portlets_html')
    manage_left_portlets_html = PageTemplateFile('zpt/manage_left_portlets', globals())

    security.declareProtected(view_management_screens, 'manage_center_portlets_html')
    manage_center_portlets_html = PageTemplateFile('zpt/manage_center_portlets', globals())

    security.declareProtected(view_management_screens, 'manage_right_portlets_html')
    manage_right_portlets_html = PageTemplateFile('zpt/manage_right_portlets', globals())

InitializeClass(PortletsTool)

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
