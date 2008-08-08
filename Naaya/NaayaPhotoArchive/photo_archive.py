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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from constants import ARCHIVE_PROPERTIES
from Products.Localizer.LocalPropertyManager import \
     LocalPropertyManager, LocalProperty

class photo_archive(LocalPropertyManager):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    sortorder = 100
    releasedate = ''

    def __init__(self, id, title, description, coverage, keywords,
                 sortorder, releasedate, lang):
        """
        Constructor.
        """
        self.id = id
        self.save_properties(title, description, coverage, keywords,
                             sortorder, releasedate, lang)

    def save_properties(self, title, description, coverage, keywords,
                        sortorder, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.releasedate = releasedate

    def copyObjects(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        id_list = self.utConvertToList(kwargs.get('ids', []))
        if not id_list:
            self.setSessionErrors(['Please select one or more items to copy.'])
        else:
            try: self.manage_copyObjects(id_list, REQUEST)
            except: self.setSessionErrors(['Error while copy data.'])
            else: self.setSessionInfo(['Item(s) copied.'])
        if REQUEST: REQUEST.RESPONSE.redirect(self.absolute_url())

    def cutObjects(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        id_list = self.utConvertToList(kwargs.get('ids', []))
        if not id_list:
            self.setSessionErrors(['Please select one or more items to cut.'])
        else:
            try: self.manage_cutObjects(id_list, REQUEST)
            except: self.setSessionErrors(['Error while cut data.'])
            else: self.setSessionInfo(['Item(s) cut.'])
        if REQUEST: REQUEST.RESPONSE.redirect(self.absolute_url())

    def pasteObjects(self, REQUEST=None):
        """ """
        if not self.checkPermissionPasteObjects():
            self.setSessionErrors(['You are not allowed to paste objects in this context.'])
        else:
            try: self.manage_pasteObjects(None, REQUEST)
            except: self.setSessionErrors(['Error while paste data.'])
            else: self.setSessionInfo(['Item(s) pasted.'])
        if REQUEST: REQUEST.RESPONSE.redirect(self.absolute_url())

    def deleteObjects(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        id_list = self.utConvertToList(kwargs.get('ids', []))
        if not id_list:
            self.setSessionErrors(['Please select one or more items to delete.'])
        else:
            try: self.manage_delObjects(id_list)
            except: self.setSessionErrors(['Error while delete data.'])
            else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect(self.absolute_url())
    #
    # Methods required by edit template
    #
    def hasVersion(self):
        """ """
        return None
    
    def sort_objects(self, sort_list=(), sort_by='sortorder', reverse=0):
        """ Sort a list of objects by given sort_by attr
        """
        return self.utSortObjsListByAttr(sort_list, sort_by, reverse)
    
    def getVersionLocalProperty(self, id, lang):
        """ """
        return self.getLocalProperty(id, lang)
    
    def getVersionProperty(self, id):
        """ """
        return getattr(self, id)
    
    def getPropertyValue(self, p_id, lang=None):
        """
        Returns a property value in the specified language.
        @param p_id: property id
        @type p_id: string
        @param lang: language code
        @type lang: string
        """
        if lang is None: lang = self.gl_get_selected_language()
        return self.getLocalProperty(p_id, lang)
    
    def del_pluggable_item_session(self, meta_type):
        for property in ARCHIVE_PROPERTIES:
            self.delSession(property)
    
    def updateSessionFrom(self, REQUEST=None, **kwargs):
        """Update session from a given language"""
        # Update kwargs from request
        if not REQUEST:
            return
        parents = REQUEST.get('PARENTS', None)
        if not parents:
            return

        doc = parents[0]
        form = getattr(REQUEST, 'form', {})
        kwargs.update(form)
        # Update session info
        from_lang = kwargs.get('from_lang', None)
        lang = kwargs.get('lang', None)

        version = getattr(doc, 'hasVersion', None) and doc.hasVersion()
        context = version and doc.version or doc
        for key, value in kwargs.items():
            value = context.getPropertyValue(key, from_lang)
            if not value:
                continue
            self.setSession(key, value)
        # Return
        REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (doc.absolute_url(), lang))
    

    style_css = PageTemplateFile('zpt/NyPhotoArchive.css.zpt', globals())
