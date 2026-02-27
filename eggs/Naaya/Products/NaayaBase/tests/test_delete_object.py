from AccessControl import Unauthorized

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.url.url_item import addNyURL

class TestDeleteByOwner(NaayaTestCase):
    """Test that owners can delete their own content.

    Owner role has 'Naaya - Delete content' permission by default
    (configured in skel.xml), so contributors can delete objects they own.
    Non-owner contributors should NOT be able to delete others' objects.
    """

    def tearDown(self):
        self.logout()

    def _submit_obj(self):
        object_id = addNyURL(self.portal['info'], 'testurl', title="URL")
        return self.portal['info'][object_id]

    def test_not_allowed(self):
        """ non-owner contributor cannot access deleteThis """
        self.login('contributor')
        ob = self._submit_obj()
        # Switch to a different contributor who is NOT the owner
        self.login('user1')
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse,
                          'info/testurl/deleteThis')

    def test_owner_can_traverse_delete(self):
        """ owner can access deleteThis via restrictedTraverse """
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

    def test_not_allowed_by_checking(self):
        """ non-owner contributor cannot delete via folder checkbox """
        self.login('contributor')
        parent = self.portal['info']
        ob = self._submit_obj()
        # Switch to a different contributor who is NOT the owner
        self.login('user1')
        self.assertRaises(Unauthorized, parent.deleteObjects, id=ob.getId())

    def test_delete_by_checking(self):
        """ test can delete own object by ticking checkbox in folder view """
        parent = self.portal['info']
        self.login('contributor')

        ob = self._submit_obj()
        ob_id = ob.getId()

        self.assertTrue(ob_id in parent.objectIds())

        parent.deleteObjects(id=ob_id)

        self.assertTrue(ob_id not in parent.objectIds())
