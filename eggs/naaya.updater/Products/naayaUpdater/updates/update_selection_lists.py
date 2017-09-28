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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateSelectionLists(UpdateScript):
    """ Migrates from selection lists to RefTrees"""
    title = 'Update from selection lists to RefTrees'
    creation_date = 'Feb 22, 2010'
    authors = ['David Batranu']
    description = 'Migrates from currently used selection lists (RefLists) to the new-style RefTrees'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        ptool = portal.getPortletsTool()
        portal_lists = ptool.getRefLists()
        for list in portal_lists:
            if list.getId().endswith('_old'):
                continue
            list_contents = list.get_list()
            self.make_reftree(portal, ptool, list, list_contents)
            self.log.debug('Migrated %s' % list.title)
        return True

    def make_reftree(self, portal, ptool, list, list_contents):
        tree = (list.id, list.title)
        tree_nodes = [(node.id, node.title) for node in list_contents]
        ptool.manage_renameObjects([list.id], ['%s_old' % list.id])
        ptool.manage_addRefTree(id=tree[0], title=tree[1])
        for node_id, node_title in tree_nodes:
            ptool[tree[0]].manage_addRefTreeNode(id=node_id, title=node_title, pickable=True)


