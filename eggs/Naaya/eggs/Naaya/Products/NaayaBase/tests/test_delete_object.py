from AccessControl import Unauthorized

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.url.url_item import addNyURL
from Products.NaayaBase.constants import PERMISSION_DELETE_OBJECTS
from naaya.core.zope2util import permission_add_role

class TestDeleteByOwner(NaayaTestCase):
    def setUp(self):
        notif_tool = self.portal.portal_notification

    def tearDown(self):
        self.logout()

    def _submit_obj(self):
        object_id = addNyURL(self.portal['info'], 'testurl', title="URL")
        return self.portal['info'][object_id]

    def test_not_allowed(self):
        self.login('contributor')

        ob = self._submit_obj()

        self.assertRaises(Unauthorized, self.portal.restrictedTraverse,
                          'info/testurl/deleteThis')

    def test_ok(self):
        permission_add_role(self.portal, PERMISSION_DELETE_OBJECTS, 'Owner')

        self.login('contributor')

        ob = self._submit_obj()

        self.portal.restrictedTraverse('info/testurl/deleteThis')

    def test_delete(self):
        ob = self._submit_obj()
        ob_id = ob.getId()
        parent = self.portal['info']

        self.assertTrue(ob_id in parent.objectIds())

        ob.deleteThis()

        self.assertTrue(ob_id not in parent.objectIds())
