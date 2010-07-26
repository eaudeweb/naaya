""" Updater tool
"""
import os, sys, types
from os.path import join, isfile

from zope.interface import implements
from zope.component import queryUtility, queryMultiAdapter

import Globals
from OFS.Folder import Folder

from Products.Naaya import NySite as NySite_module
from Products.Naaya.interfaces import INySite

import utils
from interfaces import IUpdater, IUpdateScript

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'
NAAYAUPDATER_PRODUCT_PATH = Globals.package_home(globals())

class NaayaUpdater(Folder):
    """ NaayaUpdater class """

    implements(IUpdater)

    meta_type = 'Naaya Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'
    title = UPDATERTITLE
    pmeta_types = ('Naaya Site',
                   'CHM Site',
                   'EnviroWindows Site',
                   'SEMIDE Site',
                   'SMAP Site'
                   )

    def manage_options(self):
        """ """
        return (
            {'label': 'Updates', 'action': '@@view.html'},
            {'label':'Contents', 'action':'manage_main',
             'help':('OFSP','ObjectManager_Contents.stx')},
        )

    def __bobo_traverse__(self, REQUEST, key):
        if hasattr(self, key):
            return getattr(self, key)

        util = queryUtility(IUpdateScript, name=key)
        if not util:
            raise AttributeError(key)

        script = util()
        script.id = key
        return script.__of__(self)

    # ##########################################################################
    # XXX Move following to utils
    # ##########################################################################
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
    def getPortal(self, ppath):
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(ppath)

    def getPortals(self, context=None, meta_types=None):
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
