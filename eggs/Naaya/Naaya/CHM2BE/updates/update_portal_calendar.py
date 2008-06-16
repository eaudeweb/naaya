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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web

from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.NaayaCalendar.EventCalendar import manage_addEventCalendar
from Products.CHM2.CHMSite import Extra_for_DateRangeIndex

class CustomContentUpdater(NaayaContentUpdater):
    """ """

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Remove & Add CHM portal_calendar'
        self.description = 'Replace obsolete portal_calendars with new instances for CHM Sites'
    
    def _verify_doc(self, doc):
        """ See super"""
        return doc
    
    def _list_updates(self):
        """ Return all portals that need update"""
        utool = self.aq_inner.aq_parent
        portals = utool.getPortals(meta_types=['CHM Site'])
        for portal in portals:
            if not self._verify_doc(portal):
                continue
            yield portal
    
    def _update_catalog(self, portal):
        ctool = portal.getCatalogTool()
        if 'resource_interval' not in ctool.indexes():
            try:
                extra=Extra_for_DateRangeIndex(since_field='start_date', until_field='end_date')
                ctool.manage_addIndex("resource_interval", 'DateRangeIndex', extra=extra) 
                ctool.manage_reindexIndex(ids=['resource_interval'])
            except Exception, err:
                logger.debug('Catalog:  %-50s [ERROR] %s', portal.absolute_url(1), err)
            else:
                logger.debug('Catalog:  %-50s [UPDATED]', portal.absolute_url(1))
    
    def _update_calendar(self, portal):
        if getattr(portal, 'portal_calendar', None):
            try:
                portal.manage_delObjects(['portal_calendar'])
            except Exception, err:
                logger.debug('Calendar: %-50s [ERROR] %s', portal.absolute_url(1), err)
        manage_addEventCalendar(portal, id="portal_calendar",
                                title='Calendar of Events',
                                description='', day_len='2',
                                cal_meta_types='Naaya Event',
                                start_day='Monday',
                                catalog=portal.getCatalogTool().getId(),
                                REQUEST=None)
        logger.debug('Calendar: %-50s [UPDATED]', portal.absolute_url(1))
        
    def _update(self):
        updates = self._list_updates()
        for update in updates:
            self._update_catalog(update)
            self._update_calendar(update)

def register(uid):
    return CustomContentUpdater(uid)
