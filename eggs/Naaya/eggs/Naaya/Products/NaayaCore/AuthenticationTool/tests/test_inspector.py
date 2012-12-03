from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

from Products.NaayaCore.AuthenticationTool.inspector import allowed, allowed2

class InspectorTestCase(NaayaTestCase):

    def test_allowed_view_public(self):
        self.portal._View_Permission = ['Administrator', 'Owner', 'Anonymous']
        self.assertEqual(allowed(self.portal.info, 'View'),
         {'View':
          {'Manager': ('inherited', {'source': ''}),
           'Administrator': ('inherited', {'source': '/portal'}),
           'Anonymous': ('inherited', {'source': '/portal'}),
           'Owner': ('inherited', {'source': '/portal'})}})
        self.assertEqual(allowed2(self.portal.info, 'View'),
         {'View':
          {'Administrator': ('pseudorole', {'source': 'Anonymous'}),
           'Anonymous': ('inherited', {'source': '/portal'}),
           'Authenticated': ('pseudorole', {'source': 'Anonymous'}),
           'Manager': ('pseudorole', {'source': 'Anonymous'}),
           'Owner': ('pseudorole', {'source': 'Anonymous'}),
           'Contributor': ('pseudorole', {'source': 'Anonymous'}),
           'Reviewer': ('pseudorole', {'source': 'Anonymous'})}})

    def test_allowed_view_restricted(self):
        self.portal._View_Permission = ('Administrator', 'Contributor', 'Owner')
        self.assertEqual(allowed2(self.portal.info, 'View'),
         {'View':
          {'Administrator': ('inherited', {'source': '/portal'}),
           'Owner': ('inherited', {'source': '/portal'}),
           'Contributor': ('inherited', {'source': '/portal'})}})
