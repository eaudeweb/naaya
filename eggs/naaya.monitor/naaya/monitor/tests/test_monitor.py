from io import BytesIO
from unittest.mock import patch

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.monitor import blobusage
from naaya.monitor.monitor import NaayaMonitor


def upload(parent, filename, data):
    f = BytesIO(data)
    f.filename = filename
    ob_id = parent.addNyBFile(uploaded_file=f)
    parent[ob_id].approveThis()
    return parent[ob_id]


class BlobUsageTest(NaayaTestCase):

    def test_stats(self):
        upload(self.portal.info, 'a.txt', b'12345')
        upload(self.portal.info, 'b.txt', b'123')
        stats, timestamp = blobusage.blobstorage_stats(self.app)
        self.assertEqual(stats[self.portal.getId()],
                         {'du': 8, 'objects': 2, 'versions': 2, 'extra': {}})

    def test_stats_item(self):
        upload(self.portal.info, 'a.txt', b'12345')
        self.app._setObject('naaya_monitor', NaayaMonitor('naaya_monitor'))
        monitor = self.app['naaya_monitor']
        with patch.object(blobusage.transaction, 'commit'):
            blobusage.manage_addStatsItem(monitor)
        item, = monitor.objectValues(blobusage.StatsItem.meta_type)
        from AccessControl.SecurityManagement import (newSecurityManager,
                                                      noSecurityManager)
        newSecurityManager(None, self.app.acl_users.getUser('admin')
                           .__of__(self.app.acl_users))
        self.addCleanup(noSecurityManager)
        request = self.portal.REQUEST
        request['URL1'] = item.absolute_url()
        # the ZMI tabs need a published request; only the table is tested
        with patch.object(blobusage.StatsItem, 'manage_tabs', '',
                          create=True):
            html = item.manage_workspace(request, None)
        self.assertIn(self.portal.title_or_id(), html)
        self.assertIn(self.portal.absolute_url(), html)
