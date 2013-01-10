from copy import deepcopy

from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Products.Five.browser import BrowserView

from naaya.monitor import blobusage


ID_NAAYA_MONITOR = 'naaya_monitor'
TITLE_NAAYA_MONITOR = METATYPE_NAAYA_MONITOR ='Naaya Monitor'

class NaayaMonitorAddView(BrowserView):
    """Add view for NaayaMonitor
    """

    def __call__(self):
        parent = self.context.aq_parent
        parent._setObject(ID_NAAYA_MONITOR,
                    NaayaMonitor(ID_NAAYA_MONITOR))#, TITLE_NAAYA_MONITOR))
        self.request.RESPONSE.redirect(parent.absolute_url()+'/manage_main')

class NaayaMonitor(Folder):
    """
    Persistent root-level object, storing tech statistics for Naaya sites.
    """

    meta_type = METATYPE_NAAYA_MONITOR

    folder_meta_types = [blobusage.StatsItem.meta_type]
    meta_types = (
        {'name': blobusage.StatsItem.meta_type,
         'action': 'manage_add_blobstats_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_add_blobstats_html')
    def manage_add_blobstats_html(self, REQUEST, RESPONSE):
        """ """
        return blobusage.manage_addStatsItem(self, REQUEST, RESPONSE)
