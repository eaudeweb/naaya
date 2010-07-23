from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
from Products.NaayaPhotoArchive.NyPhotoGallery import manage_addNyPhotoGallery
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.NyPhoto import NyPhoto, addNyPhoto

class UpdateSemidePhotos(UpdateScript):
    """ Update Semide Photos """
    id = 'update_semide_photos'
    title = 'Update Semide Photos'
    creation_date = DateTime('Mar 31, 2010')
    authors = ['Alexandru Plugaru']
    priority = PRIORITY['HIGH']
    description = 'Update Semide Photos from SEMIDEPhotoArchive to naaya.photoarchive'
    #dependencies = []
    categories = ['semide']

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        if portal.id == 'medaquaministerial2010':
            portal.manage_renameObjects(['photos', ], ['photos_old', ])
            photo_gallery_folder = portal.photos_old
            manage_addNyPhotoGallery(portal, id='photos', title=photo_gallery_folder.title)
            new_gallery = portal.photos
            new_gallery.tooltip = photo_gallery_folder.title
            portal.maintopics[portal.maintopics.index('photos_old')] = 'photos'

        if photo_gallery_folder:
            for photo_folder in photo_gallery_folder.objectValues():
                if photo_folder.title: new_folder_title = photo_folder.title
                else: new_folder_title = photo_folder.id

                manage_addNyPhotoFolder(new_gallery, id=photo_folder.id, title=new_folder_title)
                new_photo_folder = new_gallery._getOb(photo_folder.id)
                new_photo_folder.author = u''
                new_photo_folder.source = u''
                new_photo_folder.max_photos = 500
                folder_pics = photo_folder.objectIds()

                for prop, value in photo_folder.__dict__.items():
                    if prop not in folder_pics and prop != '_objects':
                        setattr(new_photo_folder, prop, value)

                for pic in photo_folder.objectValues():
                    if pic.title: new_pic_title = pic.title
                    else: new_pic_title = pic.id

                    new_pic_id = addNyPhoto(new_photo_folder, id=pic.id, title=new_pic_title)
                    new_pic = new_photo_folder._getOb(new_pic_id)

                    for prop, value in pic.__dict__.items():
                        if prop == '__ac_local_roles__':
                            setattr(new_pic, '_owner', (['acl_users'], value.keys()[0]))
                    extfile_original = getattr(pic, '_ext_file', None)
                    if extfile_original:
                        try:
                            extfile = getattr(new_pic, extfile_original.id)
                        except AttributeError:
                            new_pic.manage_delObjects(['find_broken_products', ])
                            extfile = extfile_original
                            extfile.__version__ = '2.0.2'
                        extfile.width = pic.width
                        extfile.height = pic.height
                        extfile.__ac_local_roles__ = new_pic.__ac_local_roles__
                        extfile.filename = extfile_original.filename
                        extfile.descr = extfile_original.descr
                        extfile._p_changed = 1

        if portal.id == 'medaquaministerial2010': #Delete old gallery folder
            portal.manage_delObjects([photo_gallery_folder.id])
        return True
