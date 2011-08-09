import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.url.url_item import addNyURL
from Products.NaayaBase.NyComments import NyComment

def physical_path(obj):
    return '/'.join(obj.getPhysicalPath())

class NyCommentsTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'folder', contributor='admin', submission=1)
        addNyURL(self.portal.folder, id='test_url', title='test url')
        transaction.commit()

    def catalog_search(self, meta_type, **kwargs):
        catalog = self.portal.getCatalogTool()
        brains = catalog(meta_type=meta_type, **kwargs)
        return [b.getObject() for b in brains]

    def test_comments_container(self):
        self.assertFalse(hasattr(self.portal.folder.test_url, '.comments'))

    def test_add_comment(self):
        self.portal.folder.test_url._comment_add(body='test comment')
        container = self.portal.folder.test_url._get_comments_container()
        self.assertEqual(len(container.objectValues()), 1)
        self.assertEqual(container.objectValues()[0].body, 'test comment')

    def test_del_comment(self):
        comment = self.portal.folder.test_url._comment_add(body='test comment')
        self.portal.folder.test_url._comment_del(comment.id)
        container = self.portal.folder.test_url._get_comments_container()
        self.assertEqual(len(container.objectValues()), 0)

    def test_catalog_comment(self):
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 0)

        comment = self.portal.folder.test_url._comment_add(body='test comment')
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 1)

        self.portal.folder.test_url._comment_del(comment.id)
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 0)

    def test_catalog_delete_commented_object(self):
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 0)

        comment = self.portal.folder.test_url._comment_add(body='test comment')
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 1)

        self.portal.folder.manage_delObjects(['test_url'])
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 0)

    def test_catalog_copy_commented_object(self):
        self.login()
        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 0)

        comment = self.portal.folder.test_url._comment_add(body='test comment')
        self.assertEqual(len(self.catalog_search(NyComment.meta_type,
                             path = physical_path(self.portal.folder))), 1)

        addNyFolder(self.portal, 'other_folder', contributor='admin', submission=1)
        clipboard = self.portal.folder.manage_copyObjects(['test_url'])
        self.portal.other_folder.manage_pasteObjects(clipboard)

        self.assertEqual(len(self.catalog_search(NyComment.meta_type,
                             path = physical_path(self.portal.other_folder))), 1)

        self.logout()

    def test_catalog_cut_commented_object(self):
        self.login()
        addNyFolder(self.portal, 'other_folder', contributor='admin', submission=1)

        self.assertEqual(len(self.catalog_search(NyComment.meta_type)), 0)

        comment = self.portal.folder.test_url._comment_add(body='test comment')
        self.assertEqual(len(self.catalog_search(NyComment.meta_type,
                             path = physical_path(self.portal.folder))), 1)

        clipboard = self.portal.folder.manage_cutObjects(['test_url'])
        self.portal.other_folder.manage_pasteObjects(clipboard)

        self.assertEqual(len(self.catalog_search(NyComment.meta_type,
                             path = physical_path(self.portal.folder))), 0)

        self.assertEqual(len(self.catalog_search(NyComment.meta_type,
                             path = physical_path(self.portal.other_folder))), 1)

        self.logout()

    def test_get_comments(self):
        first_comment = self.portal.folder.test_url._comment_add(body='test comment', 
                                                                 releasedate='2/10/2010')
        second_comment = self.portal.folder.test_url._comment_add(body='test comment',
                                                                  releasedate='1/10/2010')
        self.assertEqual(self.portal.folder.test_url.count_comments(), 2)
        self.assertEqual(self.portal.folder.test_url.get_comments_list()[0].releasedate,
                         '1/10/2010')
