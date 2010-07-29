from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.NyPhoto import NyPhoto, addNyPhoto

class UpdateRecoverPhotos(UpdateScript):
    """  """
    id = 'update_newsevents_paths'
    title='Fix missing photos in semide photo folder'
    description='Fix missing photos in semide photo folder'
    categories = ['semide']

    def _update(self, portal):
        """ """
        if portal.id == 'semide':
            old_folder = portal.thematicdirs.fol449646
            gallery = portal.thematicdirs.photos

            for photo_folder in old_folder.objectValues():
                manage_addNyPhotoFolder(gallery, id=photo_folder.id,
                                        title=photo_folder.title_or_id())
                self.log.debug('Created PhotoFolder %r' % photo_folder.id)
                new_photo_folder = gallery._getOb(photo_folder.id)
                new_photo_folder.author = u''
                new_photo_folder.source = u''
                new_photo_folder.max_photos = 500
                folder_pics = photo_folder.objectIds()

                #Setting properties
                for prop, value in photo_folder.__dict__.items():
                    if prop not in folder_pics and prop != '_objects':
                        setattr(new_photo_folder, prop, value)
                #Copying all photos
                for pic in photo_folder.objectValues():
                    new_pic = new_photo_folder._getOb(addNyPhoto(
                        new_photo_folder, id=pic.id, title=pic.title_or_id()))

                    #Set owner
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
                        #file_path = '/'.join(extfile.filename)
                        #self.log.debug('cp ${SRC}%s ${DST}%s' % (file_path, file_path))
            return True
