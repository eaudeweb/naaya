# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.NaayaPhotoArchive.NyPhotoFolder import NyPhotoFolder, manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.NyPhoto import NyPhoto, addNyPhoto

from StringIO import StringIO
#  cStringIO doesn't work! Need to see why
__version__ = '0.0.1'

class CustomContentUpdater(NaayaContentUpdater):
    """ Move NyPhotos from ZODB to local disk"""
    
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Photo Archive to version 2.0'
        self.description = 'Step 1 - Recreate photo folders/photos'
        self.update_meta_type = 'Naaya Photo Folder'

    def _verify_doc(self, doc):
        """ Check for ZODB storage """
        # Skip SEMIDE sitea as they have a different product for PhotoArchive
        if doc.getSite().meta_type == "SEMIDE Site":
            logger.debug('%-23s %s', 'Skip NyPhotoFolder', doc.absolute_url(1))
            return None
        
        if getattr(doc, '_old_id', None):
            logger.debug('%-23s %s', 'Skip NyPhotoFolder', doc.absolute_url(1))
            return None
        
        children = doc.objectValues('Naaya Photo')
        # Handle empty photo folders
        if not children:
            return doc
        
        # Handle old images in photo folders
        for child in doc.objectValues('Naaya Photo'):
            if getattr(child, 'data', ''):
                return doc
        
        logger.debug('%-23s %s', 'Skip NyPhotoFolder', doc.absolute_url(1))
        return None

    def _get_photo_local_properties(self, photo, lang=None):
        if not lang:
            lang = photo.gl_get_selected_language()
        title = photo.getVersionLocalProperty('title', lang)
        description = photo.getVersionLocalProperty('description', lang)
        author = photo.getVersionLocalProperty('author', lang)
        source = photo.getVersionLocalProperty('source', lang)
        
        # Concatenate title and description in title as description is not used anymore
        if description:
            if title == photo.getId():
                title = description
            else:
                title = ' - '.join((title, description))
        return title, author, source

    def _update_photo_folder(self, doc, old_id):
        parent = doc.getParentNode()
        lang = doc.gl_get_selected_language()
        title = doc.getVersionLocalProperty('title', lang)
        album_id = manage_addNyPhotoFolder(parent, doc.getId(), title,'', '', '',
                                           doc.sortorder, doc.releasedate, lang, '', '',
                                           doc.open_for_comments())
        album = parent._getOb(album_id)
        # To be used in step 2
        setattr(album, '_old_id', old_id)
        max_photos = len(doc.objectIds('Naaya Photo'))
        if max_photos > 100:
            setattr(album, 'max_photos', max_photos)
        # Update languages
        for language in doc.get_languages_mapping():
            lang = language['code']
            title = doc.getVersionLocalProperty('title', lang)
            if title:
                doc._setLocalPropValue('title', lang, title)
                doc.recatalogNyObject(doc)
        return album_id
    
    def _update_photo(self, doc, folder):
        if not getattr(doc, 'data', ''):
            return
        # Update default lang
        lang = doc.gl_get_selected_language()
        title, author, source = self._get_photo_local_properties(doc, lang)
        photo_id = addNyPhoto(folder, doc.getId(), title, '', doc.coverage,
                        doc.keywords, doc.sortorder, doc.releasedate, lang,
                        author, source, '', doc.open_for_comments(), doc.data)
        # Update languages
        for language in doc.get_languages_mapping():
            lang = language['code']
            title, author, source = self._get_photo_local_properties(doc, lang)
            if title:
                doc._setLocalPropValue('title', lang, title)
            if author:
                doc._setLocalPropValue('author', lang, author)
            if source:
                doc._setLocalPropValue('source', lang, source)
            if title or author or source:
                doc.recatalogNyObject(doc)
        return photo_id
    
    def _update(self):
        """ Update """
        updates = self._list_updates()
        for update in updates:
            update_id = update.getId()
            parent = update.getParentNode()
            parent.manage_renameObject(update_id, update_id + '.OLD')
            update = parent._getOb(update_id + '.OLD')
            folder_id = self._update_photo_folder(update, update_id)
            folder = parent._getOb(folder_id)
            logger.debug('Copy NaayaPhotoFolder %s => %s', update.absolute_url(1), folder.absolute_url(1))
            for photo in update.objectValues('Naaya Photo'):
                self._update_photo(photo, folder)
            logger.debug('Delete old NaayaPhotoFolder %s', update.absolute_url(1))
            parent.manage_delObjects([update.getId()])

def register(uid):
    return CustomContentUpdater(uid)
