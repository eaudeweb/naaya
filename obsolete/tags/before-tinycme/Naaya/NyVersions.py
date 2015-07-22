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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports
from os.path import join

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Product imports
from constants import *

class NyVersions:
    """
    Class for upgrading from one version to another.
    """

    security = ClassSecurityInfo()

    #generic update methods
    security.declareProtected(view_management_screens, 'reload_form')
    def reload_form(self, form_id):
        """
        Update the given form the HDD.
        """
        formstool_ob = self.getFormsTool()
        form_ob = formstool_ob._getOb(form_id, None)
        if form_ob:
            try:
                skel_path = join(self.get_data_path(), 'skel')
                content = self.futRead(join(skel_path, 'forms', '%s.zpt' % form_id), 'r')
            except:
                #the method is not overwritten - read it from Naaya
                skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
                content = self.futRead(join(skel_path, 'forms', '%s.zpt' % form_id), 'r')
            form_ob.pt_edit(text=content, content_type='')
            return 'Update form %s for website %s OK.' % (form_id, self.absolute_url())
        else:
            return 'Invalid form %s for website %s.' % (form_id, self.absolute_url())

    security.declareProtected(view_management_screens, 'reload_form')
    def reload_skin_style(self, skin_id, scheme_id, style_id):
        """
        Update the given skin's style form the HDD.
        """
        layouttool_ob = self.getLayoutTool()
        skin_ob = layouttool_ob._getOb(skin_id, None)
        if skin_ob:
            scheme_ob = skin_ob._getOb(scheme_id, None)
            if scheme_ob:
                style_ob = scheme_ob._getOb(style_id, None)
                if style_ob:
                    try:
                        skel_path = join(self.get_data_path(), 'skel')
                        content = self.futRead(join(skel_path, 'layout', skin_id, scheme_id, '%s.css' % style_id), 'r')
                    except:
                        #the method is not overwritten - read it from Naaya
                        skel_path = join(NAAYA_PRODUCT_PATH, 'skel')
                        content = self.futRead(join(skel_path, 'layout', skin_id, scheme_id, '%s.css' % style_id), 'r')
                    style_ob.pt_edit(text=content, content_type='')
                    return 'Update style %s/%s/%s for website %s OK.' % (skin_id, scheme_id, style_id, self.absolute_url())
                else:
                    return 'Invalid style %s/%s/%s for website %s.' % (skin_id, scheme_id, style_id, self.absolute_url())
            else:
                return 'Invalid scheme %s/%s for website %s.' % (skin_id, scheme_id, self.absolute_url())
        else:
            return 'Invalid skin %s for website %s.' % (skin_id, self.absolute_url())

    #specific update methods
    security.declareProtected(view_management_screens, 'upgrade_submitted')
    def upgrade_submitted(self):
        """
        Add 'submitted' property for all objects and recatalog them.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            x.submitThis()
            self.recatalogNyObject(x)

#        catalog_tool = self.getCatalogTool()
#        for b in self.getCatalogedBrains():
#            x = catalog_tool.getobject(b.data_record_id_)
#            x.submitThis()
#            self.recatalogNyObject(x)
        return "Upgrading OK: 'submitted' property added for all objects."

    security.declareProtected(view_management_screens, 'upgrade_mailfrom')
    def upgrade_mailfrom(self):
        """
        Add 'mail_address_from' property for Naaya sites
        """
        self.mail_address_from = ''
        self._p_changed = 1
        return "Upgraded OK: created email from property for portal"

    security.declareProtected(view_management_screens, 'upgrade_others')
    def upgrade_others(self):
        """
        Upgrade other stuff.
        """
        self.show_releasedate = 1
        self.submit_unapproved = 1
        self._p_changed = 1
        return "Upgraded OK: show_releasedate and submit_unapproved"

    security.declareProtected(view_management_screens, 'upgrade_photoarchive')
    def upgrade_photoarchive(self):
        """
        Upgrade other stuff.
        """
        self.PhotoArchive.submitted = 1
        self._p_changed = 1
        return "Upgraded OK: submitted for PhotoArchive"

    security.declareProtected(view_management_screens, 'upgrade_netregistry')
    def upgrade_netregistry(self):
        """
        Upgrade other stuff.
        """
        self.net_repository.submitted = 1
        self._p_changed = 1
        for site in self.net_repository.get_netsites():
            site.submitted = 1
            site._p_changed = 1
            self.recatalogNyObject(site)
            for channel in site.get_netchannels():
                channel.submitted = 1
                channel._p_changed = 1
                self.recatalogNyObject(channel)
        return "Upgraded OK: submitted for NetRepository"
            

    security.declareProtected(view_management_screens, 'set_contributor')
    def set_contributor(self, new_contributor, folder_name):
        """
        set contributor for objects with an empty string as contributor.
        """
        naaya_site = self.getSite()
        for i in naaya_site.objectValues('Naaya Folder'):
            if i.id==folder_name:
                if x.contributor=="":
                    x.setContributor(new_contributor)
        return "Contributor set up."

    security.declareProtected(view_management_screens, 'set_contributor_all')
    def change_contributor(self, old_contributor, new_contributor):
        """
        change contributor for objects.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            if x.contributor==old_contributor:
                x.setContributor(new_contributor)
                self.recatalogNyObject(x)
        return "Contributor changed."

    security.declareProtected(view_management_screens, 'set_networkportals_manager')
    def set_networkportals_manager(self):
        """
        set the network portals managers.
        """
        from managers.networkportals_manager import networkportals_manager
        networkportals_manager.__dict__['__init__'](self)
        for k, v in self.getNetworkPortals().items():
            if k.endswith('/'): k = k[:-1]
            self.add_networkportal_item(k, v, k, [])
        delattr(self, '_NySite__network_portals')
        return "Network portals managers set."

    def update_to_urls_multilingual(self, REQUEST=None):
        """ """
        catalog_tool = self.getCatalogTool()
        for url_ob in catalog_tool.query_objects_ex(meta_type="Naaya URL"):
            try:
                buf = url_ob.locator
                del url_ob.locator
                url_ob._setLocalPropValue('locator', 'en', buf)
                url_ob._p_changed = 1
            except:
                pass

InitializeClass(NyVersions)
