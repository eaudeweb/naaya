from naaya.content.base.tests.common import _IconTests
from Products.NaayaPhotoArchive.NyPhotoGallery import addNyPhotoGallery
from Products.NaayaPhotoArchive.NyPhotoFolder import addNyPhotoFolder


class PhotoGalleryIconTests(_IconTests):

    def add_object(self, parent):
        kwargs = {
            'id': 'mygallery',
            'title': 'My photo gallery',
            'submitted': 1,
            'contributor': 'contributor',
            'start_date': "10/10/2000",
        }
        ob = parent[addNyPhotoGallery(parent, **kwargs)]
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
        ob = parent[addNyPhotoFolder(parent, **kwargs)]
        ob.approveThis()
        return ob
