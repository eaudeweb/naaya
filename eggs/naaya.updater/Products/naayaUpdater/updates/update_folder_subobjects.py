from AccessControl import ClassSecurityInfo
from OFS.interfaces import IFolder

from Products.naayaUpdater.updates import UpdateScript
from Products.Naaya.interfaces import INyFolder
from naaya.core.zope2util import ofs_walk
from Products.naayaUpdater.utils import add_admin_entry
from Products.Naaya.adapters import FolderMetaTypes


class UpdateSubobjectsStatus(UpdateScript):
    """ Update folders to apply global subobject settings """
    title = 'Update folders to apply global subobject settings'
    creation_date = 'Aug 30, 2011'
    authors = ['Mihnea Simian']
    description = 'Add subobjects-dirty property'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        portal_properties = portal.getPropertiesTool()
        global_subobjects = set(portal.adt_meta_types)
        all_nyfolders = ofs_walk(portal, [INyFolder], [IFolder])
        patched = 0
        customized = 0

        for nyfolder in all_nyfolders:
            if global_subobjects != set(nyfolder.folder_meta_types):
                # subobjects are different, they were prev. modified
                # keep the folder_meta_types list as it is
                customized += 1
            else:
                # same with global, mark it with `Uses default` (None)
                fmt = FolderMetaTypes(nyfolder)
                fmt.set_values(None)
                patched += 1

        self.log.info(("%d folders now use default subobjects setting, "
                       "%d folders have subobject customizations") %
                      (patched, customized))
        if not add_admin_entry(self, portal,
                               ("""<li tal:condition="canPublish"><a """
                                """tal:attributes="href string:${site_url}/"""
                                """admin_folder_subobjects_html" title"""
                                """="Portal comments" i18n:attributes="title" """
                                """i18n:translate="">Folder subobjects</a></li>"""),
                               '${site_url}/admin_maintopics_html"'):
            self.log.error("MANUAL action: Insert link html in admin portlet")
            return False
        else:
            return True
        return True
