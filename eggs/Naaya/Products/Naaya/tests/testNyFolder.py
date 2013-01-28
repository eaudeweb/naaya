# Python
from unittest import TestSuite, makeSuite
import re
from BeautifulSoup import BeautifulSoup
from nose.plugins.skip import SkipTest

# Zope
import transaction
from Testing import ZopeTestCase
from zope import component
from AccessControl.Permissions import view
from AccessControl.Permission import Permission
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

# Products
from Products.Naaya.NyFolder import NyFolder, addNyFolder
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.interfaces import IObjectView
from Products.Naaya.adapters import (NyContentTypeViewAdapter, FolderMetaTypes,
                                     GenericViewAdapter)
from Products.NaayaCore.LayoutTool.Template import Template
from naaya.content.base.interfaces import INyContentObject

class FolderListingInfo:
    def __init__(self, browser, parent, name):
        parent_url = parent.absolute_url(1)
        soup = self.makeSoup(browser, parent_url, name)

        h1 = soup.find('h1')
        self.is_parent_restricted = '[Restricted access]' in str(h1)
        self.is_parent_limited = '[Limited access]' in str(h1)

        table = soup.find('table', id='folderfile_list')
        if table.find('tr') is not None:
            self.has_table_head = table.find('tr').find('th') is not None
        else:
            self.has_table_head = False

        # has_index_link
        index_link = table.find('a',
            attrs={'href': "http://localhost/" + parent_url + '/' + name})
        self.has_index_link = index_link is not None

        # has_checkbox
        if index_link is not None:
            tr = index_link.parent.parent

            td_checkbox = tr.find('td', attrs={'class': 'checkbox'})
            if td_checkbox is not None:
                checkbox = td_checkbox.find('input',
                        attrs={'type': 'checkbox', 'name': 'id', 'value': name})
                self.has_checkbox = checkbox is not None
            else:
                self.has_checkbox = False
        else:
            self.has_checkbox = False

        # has_icon_marked
        if index_link is not None:
            tr = index_link.parent.parent

            td_type = tr.find('td', attrs={'class': 'type'})
            if td_type is not None:
                img = td_type.find('img')
                self.has_icon_marked = img['src'].endswith('NyFolder_marked.gif')
            else:
                self.has_icon_marked = False
        else:
            self.has_icon_marked = False

        # has_edit_link
        if index_link is not None:
            tr = index_link.parent.parent

            td_edit = tr.find('td', attrs={'class': 'edit'})
            if td_edit is not None:
                edit_link = td_edit.find('a',
                        attrs={'href': "http://localhost/" + parent_url + '/' + name + "/edit_html"})
                self.has_edit_link = edit_link is not None
            else:
                self.has_edit_link = False
        else:
            self.has_edit_link = False

        # is_restricted and is_limited
        if index_link is not None:
            tr = index_link.parent.parent

            td_title = tr.find('td', attrs={'class': 'title-column'})
            if td_title is not None:
                self.is_restricted = '[Restricted access]' in str(td_title)
                self.is_limited = '[Limited access]' in str(td_title)


    def makeSoup(self, browser, url, name):
        browser.go(url)
        return BeautifulSoup(browser.get_html())




class TestNyFolderListing(NaayaFunctionalTestCase):
    def setUp(self):
        super(TestNyFolderListing, self).setUp()

        self.ancestor = self.portal.info
        self.parent_name = 'testparentfolder'
        self.parent2_name = 'testparent2folder'
        self.folder_name = 'testfolder'

        addNyFolder(self.ancestor, self.parent_name, contributor='contributor', submission=1)
        self.parent = getattr(self.ancestor, self.parent_name)

        addNyFolder(self.ancestor, self.parent2_name, contributor='contributor', submission=1)
        self.parent2 = getattr(self.ancestor, self.parent2_name)

        addNyFolder(self.parent, self.folder_name, description='mydescription', contributor='contributor', submission=1)
        self.folder = getattr(self.parent, self.folder_name)

        transaction.commit()

    def tearDown(self):
        self.ancestor.manage_delObjects([self.parent_name, self.parent2_name])
        transaction.commit()

        super(TestNyFolderListing, self).tearDown()

    def _set_del_permission(self, object, permission):
        object._Naaya___Delete_content_Permission = permission
        object._Delete_objects_Permission = permission

    def _set_edit_permission(self, object, permission):
        object._Naaya___Edit_content_Permission = permission

    def _set_copy_permission(self, object, permission):
        object._Naaya___Copy_content_Permission = permission

    def _set_paste_permission(self, object, permission):
        object._Naaya___Add_Naaya_Folder_objects_Permission = permission

    def _set_view_permission(self, object, permission):
        object._View_Permission = permission

    def _set_publish_permission(self, object, permission):
        object._Naaya___Publish_content_Permission = permission

    def _set_validate_permission(self, object, permission):
        object._Naaya___Validate_content_Permission = permission

    def _set_skip_approval_permission(self, object, permission):
        object._Naaya___Skip_approval_Permission = permission


    def test_add_folder(self):
        folder_name = 'testfolder2'

        self.browser_do_login('contributor', 'contributor')

        self.browser.go(self.parent.absolute_url(1) + '/folder_add_html')
        # check html
        html = self.browser.get_html()
        self.assertTrue('<h1>Submit Folder</h1>' in html)

        form = self.browser.get_form('frmAdd')
        #check the form
        expected_controls = set(['title:utf8:ustring',
            'description:utf8:ustring'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
                'Missing form controls: %s' %
                    repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = folder_name
        self.browser.submit()
        # check html
        html = self.browser.get_html()
        self.assertTrue('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.assertTrue(hasattr(self.parent, folder_name))
        self.assertFalse(hasattr(self.parent2, folder_name))
        folder = getattr(self.parent, folder_name)

        self.assertEqual(folder.absolute_url(), self.parent.absolute_url() + '/' + folder_name)
        self.assertEqual(folder.title_or_id(), folder_name)

        self.assertEqual(folder.icon, self.parent.icon)
        self.assertEqual(folder.icon_marked, self.parent.icon_marked)

        self.assertTrue(folder.can_be_seen() == 1)
        self.assertFalse(folder.has_restrictions())

        self.assertEqual(folder.approved, 0)

        self.browser_do_logout()


    def test_view_folder(self):
        # view folder only if approved or del_perm or copy_perm or edit_perm
        # edit link to folder only if edit_perm
        # checkbox for folder only if del_perm or copy_perm
        # if approved folder icon is icon, else folder icon is icon_marked

        self.browser_do_login('contributor', 'contributor')

        # no links in parent2
        parent2_info = FolderListingInfo(self.browser, self.parent2, self.folder_name)
        self.assertFalse(parent2_info.has_checkbox)
        self.assertFalse(parent2_info.has_index_link)
        self.assertFalse(parent2_info.has_edit_link)


        # not edit_perm, not copy_perm, not del_perm, not approved
        self._set_edit_permission(self.folder, ())
        self._set_copy_permission(self.folder, ())
        self._set_del_permission(self.folder, ())
        self.folder.approveThis(0, None)
        transaction.commit()
        # folder is in parent and not in parent2
        self.assertTrue(hasattr(self.parent, self.folder_name))
        self.assertFalse(hasattr(self.parent2, self.folder_name))
        # no links in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertFalse(parent_info.has_table_head)
        self.assertFalse(parent_info.has_checkbox)
        self.assertFalse(parent_info.has_index_link)
        self.assertFalse(parent_info.has_edit_link)


        # not edit_perm, not copy_perm, not del_perm, approved
        self.folder.approveThis(1, 'contributor')
        transaction.commit()
        # folder is in parent and not in parent2
        self.assertTrue(hasattr(self.parent, self.folder_name))
        self.assertFalse(hasattr(self.parent2, self.folder_name))
        # only index link in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertFalse(parent_info.has_checkbox)
        self.assertTrue(parent_info.has_index_link)
        self.assertFalse(parent_info.is_restricted)
        self.assertFalse(parent_info.is_limited)
        self.assertFalse(parent_info.has_icon_marked)
        self.assertFalse(parent_info.has_edit_link)


        # edit_perm, not copy_perm, not del_perm, not approved
        self.folder.approveThis(0, None)
        self._set_edit_permission(self.folder, ('Anonymous',))
        transaction.commit()
        # folder is in parent and not in parent 2
        self.assertTrue(hasattr(self.parent, self.folder_name))
        self.assertFalse(hasattr(self.parent2, self.folder_name))
        # index and edit link in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertTrue(parent_info.has_table_head)
        self.assertFalse(parent_info.has_checkbox)
        self.assertTrue(parent_info.has_index_link)
        self.assertFalse(parent_info.is_restricted)
        self.assertFalse(parent_info.is_limited)
        self.assertTrue(parent_info.has_icon_marked)
        self.assertTrue(parent_info.has_edit_link)


        # not edit_perm, not copy_perm, del_perm, not approved
        self._set_edit_permission(self.folder, ())
        self._set_del_permission(self.folder, ('Anonymous',))
        transaction.commit()
        # folder is in parent and not in parent 2
        self.assertTrue(hasattr(self.parent, self.folder_name))
        self.assertFalse(hasattr(self.parent2, self.folder_name))
        # only index link in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertTrue(parent_info.has_table_head)
        self.assertTrue(parent_info.has_checkbox)
        self.assertTrue(parent_info.has_index_link)
        self.assertFalse(parent_info.is_restricted)
        self.assertFalse(parent_info.is_limited)
        self.assertTrue(parent_info.has_icon_marked)
        self.assertFalse(parent_info.has_edit_link)


        # not edit_perm, copy_perm, not del_perm, not approved
        self._set_del_permission(self.folder, ())
        self._set_copy_permission(self.folder, ('Anonymous',))
        transaction.commit()
        # folder is in parent and not in parent 2
        self.assertTrue(hasattr(self.parent, self.folder_name))
        self.assertFalse(hasattr(self.parent2, self.folder_name))
        # only index link in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertTrue(parent_info.has_table_head)
        self.assertTrue(parent_info.has_checkbox)
        self.assertTrue(parent_info.has_index_link)
        self.assertFalse(parent_info.is_restricted)
        self.assertFalse(parent_info.is_limited)
        self.assertTrue(parent_info.has_icon_marked)
        self.assertFalse(parent_info.has_edit_link)

        # check folder description
        self.assertEqual('mydescription', self.folder.description)

        self.browser_do_logout()


    def test_delete_folder(self):
        self._set_del_permission(self.parent, ('Anonymous',))
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        self.browser.go(self.parent.absolute_url(1))
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        checkboxes = soup.findAll('input',
                attrs = {'type': 'checkbox', 'value': self.folder_name})
        self.assertEqual(len(checkboxes), 1)

        form = self.browser.get_form('objectItems')
        form['id'] = [self.folder.id]

        self.browser.clicked(form, self.browser.get_form_field(form, 'deleteObjects:method'))
        self.browser.submit()

        # folder is not in parent and not in parent 2
        self.assertFalse(hasattr(self.parent, self.folder_name))
        self.assertFalse(hasattr(self.parent2, self.folder_name))
        # no links in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertFalse(parent_info.has_index_link)
        self.assertFalse(parent_info.has_edit_link)
        # no links in parent 2
        parent2_info = FolderListingInfo(self.browser, self.parent2, self.folder_name)
        self.assertFalse(parent2_info.has_index_link)
        self.assertFalse(parent2_info.has_edit_link)

        self.browser_do_logout()


    def test_copy_paste_folder(self):
        self._set_copy_permission(self.parent, ('Anonymous',))
        self._set_paste_permission(self.parent2, ('Anonymous',))
        self._set_copy_permission(self.folder, ('Anonymous',))
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        self.browser.go(self.parent.absolute_url(1))
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        checkboxes = soup.findAll('input',
                attrs = {'type': 'checkbox', 'value': self.folder_name})
        self.assertEqual(len(checkboxes), 1)

        form = self.browser.get_form('objectItems')
        form['id'] = [self.folder.id]

        self.browser.clicked(form, self.browser.get_form_field(form, 'copyObjects:method'))
        self.browser.submit()

        self.browser.go(self.parent2.absolute_url(1))
        form = self.browser.get_form('objectItems')
        self.browser.clicked(form, self.browser.get_form_field(form, 'pasteObjects:method'))
        self.browser.submit()

        # folder is in parent and in parent 2
        self.assertTrue(hasattr(self.parent, self.folder_name))
        self.assertTrue(hasattr(self.parent2, self.folder_name))
        # index and edit links in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertTrue(parent_info.has_index_link)
        self.assertTrue(parent_info.has_edit_link)
        # index and edit links in parent 2
        parent2_info = FolderListingInfo(self.browser, self.parent2, self.folder_name)
        self.assertTrue(parent2_info.has_index_link)
        self.assertTrue(parent2_info.has_edit_link)

        self.browser_do_logout()

    def test_cut_paste_folder(self):
        self._set_copy_permission(self.parent, ('Anonymous',))
        self._set_del_permission(self.parent, ('Anonymous',))
        self._set_paste_permission(self.parent2, ('Anonymous',))
        self._set_copy_permission(self.folder, ('Anonymous',))
        self._set_del_permission(self.folder, ('Anonymous',))
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        self.browser.go(self.parent.absolute_url(1))
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        checkboxes = soup.findAll('input',
                attrs = {'type': 'checkbox', 'value': self.folder_name})
        self.assertEqual(len(checkboxes), 1)

        form = self.browser.get_form('objectItems')
        form['id'] = [self.folder.id]

        self.browser.clicked(form, self.browser.get_form_field(form, 'cutObjects:method'))
        self.browser.submit()

        self.browser.go(self.parent2.absolute_url(1))
        form = self.browser.get_form('objectItems')
        self.browser.clicked(form, self.browser.get_form_field(form, 'pasteObjects:method'))
        self.browser.submit()

        # folder is not in parent and in parent 2
        self.assertFalse(hasattr(self.parent, self.folder_name))
        self.assertTrue(hasattr(self.parent2, self.folder_name))
        # no links in parent
        parent_info = FolderListingInfo(self.browser, self.parent, self.folder_name)
        self.assertFalse(parent_info.has_index_link)
        self.assertFalse(parent_info.has_edit_link)
        # index and edit links in parent 2
        parent2_info = FolderListingInfo(self.browser, self.parent2, self.folder_name)
        self.assertTrue(parent2_info.has_index_link)
        self.assertTrue(parent2_info.has_edit_link)

        self.browser_do_logout()

    def test_cut_paste_inside_folder(self):

        from AccessControl import getSecurityManager

        self._set_skip_approval_permission(self.portal.info, ('Contributor',))
        self.portal._set_edit_own_content(edit_own_content=True)
        transaction.commit()

        #login
        self.browser_do_login('contributor', 'contributor')
        logged_user = getSecurityManager().getUser()

        #add folders
        addNyFolder(self.portal.info, 'test_folder')
        addNyFolder(self.portal.info, 'target_folder')

        # Change the ownership to the logged user
        self.portal.info.test_folder.changeOwnership(logged_user)
        self.portal.info.target_folder.changeOwnership(logged_user)

        transaction.commit()

        #go to parent folder. Ckeck if the `Owner` role has permission to copy&cut folders.
        self.browser.go(self.portal.info.absolute_url(1))
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        checkboxes = soup.findAll('input', attrs = {'type': 'checkbox',
                                                    'value': 'test_folder'})
        self.assertEqual(len(checkboxes), 1)

        #copy test_folder in clipboard
        form = self.browser.get_form('objectItems')
        form['id'] = ['test_folder']
        self.browser.clicked(form, self.browser.get_form_field(form, 'cutObjects:method'))
        self.browser.submit()

        #paste clipboard data
        self.browser.go(self.portal.info.target_folder.absolute_url(1))
        form = self.browser.get_form('objectItems')
        self.browser.clicked(form, self.browser.get_form_field(form, 'pasteObjects:method'))
        self.browser.submit()

        #test if test_folder was copied inside target_folder
        self.assertEqual(self.portal.info.target_folder.objectIds(), ['test_folder'])

        #test if test_folder was removed from the initial location
        self.assertTrue(getattr(self.portal.info, 'test_folder', None) is None)

    def test_rename_inside_folder(self):

        from AccessControl import getSecurityManager

        self._set_skip_approval_permission(self.portal.info, ('Contributor',))
        self.portal._set_edit_own_content(edit_own_content=True)
        self.portal.rename_id = True
        transaction.commit()

        #login
        self.browser_do_login('contributor', 'contributor')
        logged_user = getSecurityManager().getUser()

        #add folders
        addNyFolder(self.portal.info, 'test_folder')

        # Change the ownership to the logged user
        self.portal.info.test_folder.changeOwnership(logged_user)

        transaction.commit()

        #go to parent folder. Ckeck if the `Owner` role has permission to copy&cut folders.
        self.browser.go(self.portal.info.absolute_url(1))
        html = self.browser.get_html()
        soup = BeautifulSoup(html)
        checkboxes = soup.findAll('input', attrs = {'type': 'checkbox',
                                                    'value': 'test_folder'})
        self.assertEqual(len(checkboxes), 1)

        #rename test_folder
        form = self.browser.get_form('objectItems')
        form['id'] = ['test_folder']
        self.browser.clicked(form, self.browser.get_form_field(form, 'renameobject_html:method'))
        self.browser.submit()

        form = self.browser.get_form('renameObjects')
        form['new_ids:list'] = 'renamed_test_folder'
        self.browser.clicked(form, self.browser.get_form_field(form, 'renameBtn'))
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('Items(s) succesfully renamed' in html)

        #test if test_folder was renamed
        self.assertEqual(hasattr(self.portal.info, 'renamed_test_folder'), True)


    def test_view_adapter(self):
        self.assertTrue(INyContentObject.providedBy(self.portal.info))
        adapter = component.queryAdapter(self.portal.info, IObjectView)
        self.assertTrue(adapter is not None)
        self.assertTrue(isinstance(adapter, NyContentTypeViewAdapter))


class TestNyFolderPublicInterface(NaayaFunctionalTestCase):
    def setUp(self):
        super(TestNyFolderPublicInterface, self).setUp()

        addNyFolder(self.portal.info,
                    'testfolder',
                    contributor='contributor',
                    submission=1)
        self.folder = self.portal.info.testfolder
        transaction.commit()

    def tearDown(self):
        self.portal.info.manage_delObjects(['testfolder'])
        transaction.commit()

        super(TestNyFolderPublicInterface, self).tearDown()

    def test_lookup_custom_index(self):
        folder = self.folder

        # initially, nothing is set
        assert folder.get_custom_index_template() is None
        assert folder.compute_custom_index_value() == ''

        # test old-style `publicinterface` property
        folder.publicinterface = 1
        assert folder.compute_custom_index_value() == 'local:index'
        assert folder.get_custom_index_template() is None
        manage_addPageTemplate(folder, id='index', title='', text="hello1")
        transaction.commit()
        assert folder.get_custom_index_template() == folder.index
        self.browser.go('http://localhost/portal/info/testfolder')
        assert self.browser.get_html().strip() == "hello1"

        # new-style custom_index, locally in folder
        manage_addPageTemplate(folder, id='something', title='', text="hello2")
        folder.custom_index = 'local:something'
        assert folder.compute_custom_index_value() == 'local:something'
        transaction.commit()
        assert folder.get_custom_index_template() == folder.something
        self.browser.go('http://localhost/portal/info/testfolder')
        assert self.browser.get_html().strip() == "hello2"

        # new-style custom_index, in portal_forms
        portal_forms = self.portal.portal_forms
        portal_forms._setObject('something-else',
                        Template(id='something-else', title="",
                                 text="hello3", content_type='text/html'))
        folder.custom_index = 'site:portal_forms/something-else'
        assert (folder.compute_custom_index_value() ==
                'site:portal_forms/something-else')
        transaction.commit()
        assert (folder.get_custom_index_template() ==
                portal_forms['something-else'])
        self.browser.go('http://localhost/portal/info/testfolder')
        assert self.browser.get_html().strip() == "hello3"

    def test_custom_index(self):
        # index was not created
        self.assertTrue('index' not in self.folder.objectIds())

        # create public interface
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_edit_html')

        form = self.browser.get_form('frmEdit')
        form['custom_index'] = 'local:index'
        form_field = self.browser.get_form_field(form, 'custom_index')
        self.browser.clicked(form, form_field)
        self.browser.submit()

        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_create_custom_template')

        self.browser_do_logout()

        # index gets created
        self.assertTrue('index' in self.folder.objectIds())
        # index page is the same as folder_index
        self.browser.go('http://localhost/portal/info/testfolder')
        html = self.browser.get_html()
        self.assertTrue('testfolder' in html)

        # change custom index
        self.folder.index.write('')
        transaction.commit()

        # index page is the same as the custom index
        self.browser.go('http://localhost/portal/info/testfolder')
        html = self.browser.get_html()
        self.assertTrue('testfolder' not in html)

        # remove public interface
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_edit_html')

        form = self.browser.get_form('frmEdit')
        form['custom_index'] = ''
        form_field = self.browser.get_form_field(form, 'custom_index')
        self.browser.clicked(form, form_field)
        self.browser.submit()

        self.browser_do_logout()

        # index still there
        self.assertTrue('index' in self.folder.objectIds())
        # index page back to folder_index
        self.browser.go('http://localhost/portal/info/testfolder')
        html = self.browser.get_html()
        self.assertTrue('testfolder' in html)

    def test_portal_form(self):
        # index was not created
        self.assertTrue('index' not in self.folder.objectIds())
        # index page is the same as folder_index
        self.browser.go('http://localhost/portal/info/testfolder')
        html = self.browser.get_html()
        self.assertTrue('Restrictions' not in html)

        # create public interface
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_edit_html')

        form = self.browser.get_form('frmEdit')
        form['custom_index'] = 'site:portal_forms/folder_restrict'
        form_field = self.browser.get_form_field(form, 'custom_index')
        self.browser.clicked(form, form_field)
        self.browser.submit()

        self.browser_do_logout()

        # index doesn't get created
        self.assertTrue('index' not in self.folder.objectIds())
        # index page is not the same as folder_index
        self.browser.go('http://localhost/portal/info/testfolder')
        html = self.browser.get_html()
        self.assertTrue('Restrictions' in html)

        # remove public interface
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_edit_html')

        form = self.browser.get_form('frmEdit')
        form['custom_index'] = ''
        form_field = self.browser.get_form_field(form, 'custom_index')
        self.browser.clicked(form, form_field)
        self.browser.submit()

        self.browser_do_logout()

        # index still not there
        self.assertTrue('index' not in self.folder.objectIds())
        # index page back to folder_index
        self.browser.go('http://localhost/portal/info/testfolder')
        html = self.browser.get_html()
        self.assertTrue('Restrictions' not in html)

    def test_form_save(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        form['custom_index'] = 'site:portal_forms/folder_restrict'
        form_field = self.browser.get_form_field(form, 'custom_index')
        self.browser.clicked(form, form_field)
        self.browser.submit()

        self.browser.go('http://localhost/portal/info/testfolder'
                        '/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['custom_index'], 'site:portal_forms/folder_restrict')

        self.browser_do_logout()

class TestNyFolderSubobjects(NaayaTestCase):

    def setUp(self):
        super(TestNyFolderSubobjects, self).setUp()
        addNyFolder(self.portal.info, 'subfolder0', contributor='contributor',
                    submission=1)
        addNyFolder(self.portal.info, 'subfolder1', contributor='contributor',
                    submission=1)

    def test_folders_created_with_default_subobjects(self):
        for i in range(2):
            folder = getattr(self.portal.info, 'subfolder' + str(i))
            fmt = FolderMetaTypes(folder)
            self.assertFalse(fmt.has_custom_value)
            self.assertEqual(set(fmt.get_values()),
                             set(self.portal.adt_meta_types))

    def test_subobjects_customization(self):
        # customize one subfolder
        self.portal.info.subfolder1.manageSubobjects(subobjects=[],
                                               ny_subobjects=['Naaya Document'])
        # change global setting
        portal_properties = self.portal.getPropertiesTool()
        portal_properties.manageSubobjects([], ['Naaya Calendar'])
        fmt0 = FolderMetaTypes(self.portal.info.subfolder0)
        fmt1 = FolderMetaTypes(self.portal.info.subfolder1)
        # check
        self.assertEqual(set(fmt0.get_values()), set(['Naaya Calendar']))
        self.assertFalse(fmt0.has_custom_value)
        self.assertEqual(set(fmt1.get_values()), set(['Naaya Document']))
        self.assertTrue(fmt1.has_custom_value)
