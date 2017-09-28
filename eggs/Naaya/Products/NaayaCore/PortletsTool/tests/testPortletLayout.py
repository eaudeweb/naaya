from unittest import TestSuite, makeSuite
from copy import deepcopy
import re

from Testing import ZopeTestCase
import transaction

from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaCore.PortletsTool.PortletsTool import PortletsTool
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class PortletArrangementUnitTestCase(ZopeTestCase.TestCase):
    """ Unit tests for Naaya Portlet arrangement """

    def afterSetUp(self):
        pp = PortletsTool('portal_portlets', 'Portal portlets')
        pp.assign_portlet('', 'left', 'my_left_portlet')
        pp.assign_portlet('fol2', 'right', 'my_right_portlet')
        pp.assign_portlet('fol3', 'center', 'my_center_portlet')
        self.portal_portlets = pp

    def test_add_get(self):
        pp = self.portal_portlets
        ids = pp.get_portlet_ids_for

        self.failUnlessEqual(ids('', 'left'), ['my_left_portlet'])
        self.failUnlessEqual(ids('', 'right'), [])
        self.failUnlessEqual(ids('', 'center'), [])

        self.failUnlessEqual(ids('fol1', 'left'), ['my_left_portlet'])
        self.failUnlessEqual(ids('fol1', 'right'), [])
        self.failUnlessEqual(ids('fol1', 'center'), [])

        self.failUnlessEqual(ids('fol2', 'left'), ['my_left_portlet'])
        self.failUnlessEqual(ids('fol2', 'right'), ['my_right_portlet'])
        self.failUnlessEqual(ids('fol2', 'center'), [])

        self.failUnlessEqual(ids('fol3', 'left'), ['my_left_portlet'])
        self.failUnlessEqual(ids('fol3', 'right'), [])
        self.failUnlessEqual(ids('fol3', 'center'), ['my_center_portlet'])

    def test_remove(self):
        pp = self.portal_portlets
        ids = pp.get_portlet_ids_for

        pp.unassign_portlet('fol2', 'right', 'my_right_portlet')
        self.failUnlessEqual(pp.get_portlet_ids_for('fol2', 'right'), [])

        try:
            pp.unassign_portlet('fol2', 'right', 'my_right_portlet')
            self.fail('Should have raised ValueError')
        except ValueError, e:
            self.failUnless('No portlet named "my_right_portlet" '
                'among "right" portlets at "fol2"' in str(e))

    def test_inheritance(self):
        pp = self.portal_portlets
        ids = pp.get_portlet_ids_for

        self.failUnlessEqual(ids('fol1', 'left'), ['my_left_portlet'])
        self.failUnlessEqual(ids('fol1/subfol', 'left'), ['my_left_portlet'])

        pp.assign_portlet('fol1', 'right', '49238', inherit=False)
        self.failUnlessEqual(ids('fol1', 'right'), ['49238'])
        self.failUnlessEqual(ids('fol1/subfol', 'right'), [])

    def test_duplicate(self):
        pp = self.portal_portlets
        ids = pp.get_portlet_ids_for

        try:
            pp.assign_portlet('fol2', 'right', 'my_right_portlet')
            self.fail('Should have raised ValueError')
        except ValueError, e:
            self.failUnless('Portlet "my_right_portlet" already assigned '
                'to "right" at "fol2"')

        try:
            pp.assign_portlet('fol2', 'right', 'my_right_portlet', inherit=False)
            self.fail('Should have raised ValueError')
        except ValueError, e:
            self.failUnless('Portlet "my_right_portlet" already assigned '
                'to "right" at "fol2"')

    def test_homepage(self):
        pp = self.portal_portlets
        ids = pp.get_portlet_ids_for

        pp.assign_portlet('', 'center', '2134', inherit=False)
        self.failUnlessEqual(ids('', 'center'), ['2134'])

class FunctionalSetupMixin(object):
    def afterSetUp(self):
        addNyFolder(self.portal, id='fol', title='Folderr',
            contributor='contributor', submitted=1)
        addNyFolder(self.portal.fol, id='sub', title='Subfolderr',
            contributor='contributor', submitted=1)
        self.portal.fol.approved = 1
        portal_portlets = self.portal.portal_portlets
        self.original_portlets_layout = deepcopy(portal_portlets._portlet_layout)
        portal_portlets.addHTMLPortlet('prt1', 'Test Portlet 1')
        portal_portlets.addHTMLPortlet('prt2', 'Test Portlet 2')
        self.portal.maintopics.append('portal/fol')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.maintopics.remove('portal/fol')
        self.portal.manage_delObjects(['fol'])
        portal_portlets = self.portal.portal_portlets
        portal_portlets.manage_delObjects(['prt1', 'prt2'])
        portal_portlets._portlet_layout = self.original_portlets_layout
        transaction.commit()

class PortletArrangementTestCase(FunctionalSetupMixin, NaayaFunctionalTestCase):
    def _get(self, page):
        self.browser.go('http://localhost/' + page)
        return self.browser.get_html()

    def test_rightPortlets(self):
        self.failIf('Test Portlet' in self._get('portal'))
        self.failIf('Test Portlet' in self._get('portal/fol'))
        self.failIf('Test Portlet' in self._get('portal/fol/sub'))

        self.portal.portal_portlets.assign_portlet('', 'right', 'prt1')
        self.portal.portal_portlets.assign_portlet('fol', 'right', 'prt2')
        transaction.commit()

        self.failUnless('Test Portlet 1' in self._get('portal'))
        self.failIf('Test Portlet 2' in self._get('portal'))

        self.failUnless('Test Portlet 1' in self._get('portal/fol'))
        self.failUnless('Test Portlet 2' in self._get('portal/fol'))

        self.failUnless('Test Portlet 1' in self._get('portal/fol/sub'))
        self.failUnless('Test Portlet 2' in self._get('portal/fol/sub'))

    def test_leftPortlets(self):
        self.failIf('Test Portlet' in self._get('portal'))
        self.failIf('Test Portlet' in self._get('portal/fol'))
        self.failIf('Test Portlet' in self._get('portal/fol/sub'))

        self.portal.portal_portlets.assign_portlet('', 'left', 'prt1')
        self.portal.portal_portlets.assign_portlet('fol', 'left', 'prt2')
        transaction.commit()

        self.failUnless('Test Portlet 1' in self._get('portal'))
        self.failIf('Test Portlet 2' in self._get('portal'))

        self.failUnless('Test Portlet 1' in self._get('portal/fol'))
        self.failUnless('Test Portlet 2' in self._get('portal/fol'))

        self.failUnless('Test Portlet 1' in self._get('portal/fol/sub'))
        self.failUnless('Test Portlet 2' in self._get('portal/fol/sub'))

    def test_centerPortlets(self):
        self.failIf('Test Portlet' in self._get('portal'))
        self.failIf('Test Portlet' in self._get('portal/fol'))
        self.failIf('Test Portlet' in self._get('portal/fol/sub'))

        self.portal.portal_portlets.assign_portlet('', 'center', 'prt1')
        self.portal.portal_portlets.assign_portlet('fol', 'center', 'prt2')
        transaction.commit()

        self.failUnless('Test Portlet 1' in self._get('portal'))
        self.failIf('Test Portlet 2' in self._get('portal'))

        self.failUnless('Test Portlet 1' in self._get('portal/fol'))
        self.failUnless('Test Portlet 2' in self._get('portal/fol'))

        self.failUnless('Test Portlet 1' in self._get('portal/fol/sub'))
        self.failUnless('Test Portlet 2' in self._get('portal/fol/sub'))

    def test_default_portlets(self):
        homepage = self._get('portal')
        folder = self._get('portal/fol')
        info = self._get('portal/info')

        if self.portal.getSyndicationTool().latestnews_rdf.get_objects_for_rdf():
            self.failUnless('Latest news' in homepage)
        self.failIf('Latest news' in folder)
        self.failIf('Latest news' in info)

        if self.portal.getSyndicationTool().upcomingevents_rdf.get_objects_for_rdf():
            self.failUnless('Upcoming events' in homepage)
        self.failIf('Upcoming events' in folder)
        self.failIf('Upcoming events' in info)

        if self.portal.getSyndicationTool().latestuploads_rdf.get_objects_for_rdf():
            self.failUnless('Latest uploads' in homepage)
        self.failIf('Latest uploads' in folder)
        self.failIf('Latest uploads' in info)

        # test "Main sections"
        self.failUnless('Folderr' in homepage)
        self.failUnless('Folderr' in folder)
        self.failUnless('Folderr' in info)

class PortletAdminFunctionalTestCase(FunctionalSetupMixin, NaayaFunctionalTestCase):

    def test_assignPortletInherited(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/portal_portlets/admin_layout')
        form = self.browser.get_form('assign_portlet')

        self.browser.clicked(form, form.find_control('location'))
        form['location'] = 'portal/fol'
        form['portlet_id'] = ['prt1']
        form['position'] = ['center']
        self.browser.submit()

        self.failUnless('Successfully assigned portlet "Test Portlet 1" '
            'at "fol"' in self.browser.get_html())

        portlet_layout = self.portal.portal_portlets._portlet_layout
        self.failUnless(('fol', 'center') in portlet_layout)
        self.failUnlessEqual(portlet_layout[('fol', 'center')],
            [{'id': 'prt1', 'inherit': True}])

        self.browser_do_logout()

    def test_assignPortletNonInherited(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/portal_portlets/admin_layout')
        form = self.browser.get_form('assign_portlet')

        self.browser.clicked(form, form.find_control('location'))
        form['location'] = 'portal/fol'
        form['portlet_id'] = ['prt1']
        form['position'] = ['center']
        form['inherit:boolean'] = []
        self.browser.submit()

        self.failUnless('Successfully assigned portlet "Test Portlet 1" '
            'at "fol"' in self.browser.get_html())

        portlet_layout = self.portal.portal_portlets._portlet_layout
        self.failUnless(('fol', 'center') in portlet_layout)
        self.failUnlessEqual(portlet_layout[('fol', 'center')],
            [{'id': 'prt1', 'inherit': False}])

        self.browser_do_logout()

    def test_assignPortletForm(self):
        self.browser.go('http://localhost/portal/portal_portlets/admin_layout')
        self.assertRedirectLoginPage()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/portal_portlets/admin_layout')
        form = self.browser.get_form('assign_portlet')

        position_items = set(item.name
            for item in form.find_control('position').items)
        self.failUnlessEqual(position_items, set(['left', 'center', 'right']))
        portlet_id_items = set(item.name
            for item in form.find_control('portlet_id').items)
        self.failUnless(set(['prt1', 'prt2']).issubset(portlet_id_items))

        self.browser_do_logout()

    def test_unassignPortlet(self):
        self.portal.portal_portlets.assign_portlet('fol', 'right', 'prt2')
        transaction.commit()

        self.browser.go('http://localhost/portal/fol')
        self.failUnless('Test Portlet 2' in self.browser.get_html())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/portal_portlets/admin_layout')

        for form in self.browser._browser.forms():
            # look at each form; stop when we find the one that deletes our portlet
            try:
                if form['portlet_id'] != 'prt2': continue
                if form['location'] != 'fol': continue
                if form['position'] != 'right': continue
                if form['action'] != 'Unassign': continue
            except: # one of the form fields is missing
                continue
            break # found it!
        else:
            self.fail('Could not find "Remove" button for our portlet')

        self.browser.clicked(form, form.find_control('action'))
        self.browser.submit()
        self.failUnless('Successfully removed portlet "Test Portlet 2" '
            'from "fol"' in self.browser.get_html())
        self.browser_do_logout()

        self.browser.go('http://localhost/portal/fol')
        self.failIf('Test Portlet 2' in self.browser.get_html())
