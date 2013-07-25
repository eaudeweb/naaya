from mock import Mock

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.constants import PERMISSION_SKIP_APPROVAL
from naaya.content.url.url_item import addNyURL
from naaya.core.zope2util import permission_add_role

class TestApproval(NaayaTestCase):
    def setUp(self):
        self.notify_maintainer = self.portal.getNotificationTool().notify_maintainer = Mock()

    def tearDown(self):
        self.logout()

    def _submit_obj(self):
        object_id = addNyURL(self.portal['info'], 'testurl', title="URL")
        return self.portal['info'][object_id]

    def test_submit_by_contributor(self):
        self.login('contributor')

        ob = self._submit_obj()

        self.assertEqual(ob.approved, 0)
        self.assertEqual(ob.submitted, 1)
        self.assertEqual(self.notify_maintainer.call_count, 1)

    def test_submit_by_contributor_with_auto_approve(self):
        permission_add_role(self.portal, PERMISSION_SKIP_APPROVAL,
                            'Contributor')
        self.login('contributor')

        ob = self._submit_obj()

        self.assertEqual(ob.approved, 1)
        self.assertEqual(ob.submitted, 1)
        self.assertTrue(self.notify_maintainer.call_count, 1)

    def test_submit_by_manager(self):
        self.login('site_admin')

        ob = self._submit_obj()

        self.assertEqual(ob.approved, 1)
        self.assertEqual(ob.submitted, 1)
        self.assertTrue(self.notify_maintainer.call_count, 1)

class TestApprovalForFolder(TestApproval):
    def _submit_obj(self):
        object_id = addNyFolder(self.portal['info'], 'testfol', title="Fol")
        return self.portal['info'][object_id]
