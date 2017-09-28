from AccessControl.Permission import Permission
from AccessControl.Permissions import view

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class PortalLayoutTest(NaayaTestCase):

    def test_security(self):
        """ test portal_layout is visible by Anonymous """
        portal_layout = self.portal.getLayoutTool()
        view_perm = Permission(view, (), portal_layout)
        assert 'Anonymous' in view_perm.getRoles()
