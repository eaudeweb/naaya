import os
import sys
import types
from zope.interface import implements
from os.path import join, isfile

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
import Globals

from Products.Naaya import NySite as NySite_module
from Products.naayaUpdater import utils

from Products.Naaya.interfaces import INySite
from Products.naayaUpdater import update_scripts
from discover import get_module_names, get_module_objects, filter_subclasses

from interfaces import IUpdater

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'
NAAYAUPDATER_PRODUCT_PATH = Globals.package_home(globals())

class NaayaUpdater(Folder):
    """ NaayaUpdater class """

    implements(IUpdater)

    meta_type = 'Naaya Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'
    update_scripts = {}
    scripts_packages = ['Products.naayaUpdater.update_scripts']

    def manage_options(self):
        """ """
        return (
            {'label': 'Updates', 'action': '@@view.html'},
            {'label':'Contents', 'action':'manage_main',
             'help':('OFSP','ObjectManager_Contents.stx')},
        )

    security = ClassSecurityInfo()

    def __init__(self, id):
        """ """
        self.id = id
        self.title = UPDATERTITLE
        self.pmeta_types = ['Naaya Site', 'CHM Site', 'EnviroWindows Site',
                            'SEMIDE Site', 'SMAP Site']
        self.refresh_updates_dict()

    def __bobo_traverse__(self, REQUEST, key):
        if hasattr(self, key):
            return getattr(self, key)
        if key in NaayaUpdater.update_scripts:
            return NaayaUpdater.update_scripts[key]().__of__(self)

    def refresh_updates_dict(self):
        NaayaUpdater.update_scripts = {}
        for package in self.scripts_packages:
            scripts = self.get_updates_from_module(package)
            for s in scripts:
                self.register_update_script(s.id, s)

    def register_update_script(self, key, update_script):
        NaayaUpdater.update_scripts[key] = update_script

    security.declareProtected(view_management_screens, 'get_updates')
    def get_updates(self):
        return NaayaUpdater.update_scripts

    def update_ids(self): #
        return sorted(NaayaUpdater.update_scripts.keys())

    security.declareProtected(view_management_screens, 'get_updates_from_module')
    def get_updates_from_module(self, module_path):
        """ """
        try:
            module_names = get_module_names(module_path, 'update_.*')
            update_cls = []
            for name in module_names:
                try:
                    obj_list = get_module_objects(name)
                    obj_list = filter_subclasses(obj_list, update_scripts.UpdateScript)
                    update_cls.extend(obj_list)
                except Exception, e:
                    print 'Skipping module "%s" - %s' % (name, str(e))

            return update_cls
        except Exception, e:
            print 'Skipping path "%s" - %s' % (module_path, str(e))
            return []
    security.declareProtected(view_management_screens, 'get_updates_categories')
    def get_updates_categories(self, module_path):
        """ Get all update_*.py from update_scripts and group them by category
        and order by priority.

        """
        try:
            module_names = get_module_names(module_path, 'update_.*')
            update_cls = {'Other': []} #Category->update_script
            for name in module_names:
                try:
                    obj_list = get_module_objects(name)
                    obj_list = filter_subclasses(obj_list,
                                                 update_scripts.UpdateScript)
                    for obj in obj_list:
                        if not obj.categories:
                            update_cls['Other'].append(obj)
                        else:
                            for category in obj.categories:
                                if not update_cls.has_key(category):
                                    update_cls[category] = []
                                update_cls[category].append(obj)
                except Exception, e:
                    print 'Skipping module "%s" - %s' % (name, str(e))
            #Sort by priority
            for category, cls_list in update_cls.items():
                update_cls[category] = sorted(cls_list,
                                            key=lambda x: x.priority)
            return update_cls
        except Exception, e:
            print 'Skipping path "%s" - %s' % (module_path, str(e))
            return []
    #
    # General stuff
    #
    security.declarePrivate('get_portal_path')
    def get_portal_path(self, portal):
        """
            return the portal path given the metatype
        """
        if isinstance(portal, types.ModuleType):
            m = portal
        else:
            if isinstance(portal, NySite_module.NySite):
                portal = portal.__class__
            m = sys.modules[portal.__module__]
        return os.path.dirname(m.__file__)

    security.declarePrivate('get_contenttype_content')
    def get_contenttype_content(self, id, portal):
        """
            return the content of the filesystem content-type template
        """
        portal_path = self.get_portal_path(portal)
        data_path = join(portal_path, 'skel', 'forms')

        for meta_type in portal.get_pluggable_metatypes():
            pitem = portal.get_pluggable_item(meta_type)
            #load pluggable item's data
            for frm in pitem['forms']:
                if id == frm:
                    frm_name = '%s.zpt' % frm
                    if isfile(join(data_path, frm_name)):
                        #load form from the 'forms' directory because it si customized
                        return utils.readFile(join(data_path, frm_name), 'r')
                    else:
                        #load form from the pluggable meta type folder
                        return utils.readFile(join(pitem['package_path'], 'zpt', frm_name), 'r')
                    break

    #External  ???
    security.declareProtected(view_management_screens, 'getPortal')
    def getPortal(self, ppath):
        """ """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(ppath)

    security.declareProtected(view_management_screens, 'getPortals')
    def getPortals(self, context=None, meta_types=None):
        """
            return the portals list
        """
        if context is None:
            context = self.getPhysicalRoot()
        res = []
        for ob in context.objectValues():
            if not INySite.providedBy(ob):
                continue
            if meta_types is not None and ob.meta_type not in meta_types:
                continue
            res.append(ob)
            res.extend(self.getPortals(ob, meta_types))
        return res

Globals.InitializeClass(NaayaUpdater)
