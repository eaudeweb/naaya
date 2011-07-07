from naaya.content.base.tests.common import _IconTests
from Products.NaayaPhotoArchive.NyPhotoGallery import manage_addNyPhotoGallery
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder


class PhotoGalleryIconTests(_IconTests):

    def add_object(self, parent):
        kwargs = {
            'id': 'mygallery',
            'title': 'My photo gallery',
            'submitted': 1,
            'contributor': 'contributor',
            'start_date': "10/10/2000",
        }
        ob = parent[manage_addNyPhotoGallery(parent, **kwargs)]
        ob.approveThis()
        return ob


class PhotoFolderIconTests(_IconTests):

    def add_object(self, parent):
        kwargs = {
            'id': 'myfolder',
            'title': 'My photo folder',
            'submitted': 1,
            'contributor': 'contributor',
            'start_date': "10/10/2000",
        }
        ob = parent[manage_addNyPhotoFolder(parent, **kwargs)]
        ob.approveThis()
        return ob
