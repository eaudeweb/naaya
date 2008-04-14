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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web

#Python imports
from copy import deepcopy

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from geopoint_item import geopoint_item

#module constants
METATYPE_OBJECT = 'Naaya GeoPoint'
LABEL_OBJECT = 'GeoPoint'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya GeoPoint objects'
OBJECT_FORMS = ['geopoint_add', 'geopoint_edit', 'geopoint_index', 'marker_popup']
OBJECT_CONSTRUCTORS = ['manage_addNyGeoPoint_html', 'geopoint_add_html', 'addNyGeoPoint', 'importNyGeoPoint']
OBJECT_ADD_FORM = 'geopoint_add_html'
DESCRIPTION_OBJECT = 'This is Naaya GeoPoint type.'
PREFIX_OBJECT = 'geo'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'longitude':    (1, MUST_BE_POSITIV_FLOAT, 'The Longitude field must have a value'),
    'latitude':     (1, MUST_BE_POSITIV_FLOAT, 'The Latitude field must have a value'),
    'address':      (0, '', ''),
    'geo_type':     (0, '', ''),
    'url':          (0, '', ''),
    'pointer':      (0, '', ''),
    'lang':         (0, '', '')
}

manage_addNyGeoPoint_html = PageTemplateFile('zpt/geopoint_manage_add', globals())
manage_addNyGeoPoint_html.kind = METATYPE_OBJECT
manage_addNyGeoPoint_html.action = 'addNyGeoPoint'

def geopoint_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyGeoPoint'}, 'geopoint_add')

def addNyGeoPoint(self, id='', title='', description='', coverage='', keywords='', sortorder='', longitude='', latitude='', address='', geo_type='', url='', pointer='',
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create an Contact type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'geopoint_manage_add' or l_referer.find('geopoint_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, longitude=longitude, latitude=latitude, address=address, geo_type=geo_type, url=url, pointer=pointer)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NyGeoPoint(id, title, description, coverage, keywords, sortorder, longitude, latitude, address, geo_type, url, pointer, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is None:
            return ob
        else:
            if l_referer == 'geopoint_manage_add' or l_referer.find('geopoint_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'geopoint_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, coverage=coverage, \
                keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, longitude=longitude, \
                latitude=latitude, address=address, geo_type=geo_type, url=url, pointer=pointer, lang=lang)
            REQUEST.RESPONSE.redirect('%s/geopoint_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNyGeoPoint(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param == 3:
        #just try to delete the object
        try: self.manage_delObjects([id])
        except: pass
    else:
        ob = self._getOb(id, None)
        if param in [0, 1] or (param==2 and ob is None):
            if param == 1:
                #delete the object if exists
                try: self.manage_delObjects([id])
                except: pass
            addNyGeoPoint(self, id=id,
                longitude=attrs['longitude'].encode('utf-8'),
                latitude=attrs['latitude'].encode('utf-8'),
                address=attrs['address'].encode('utf-8'),
                geo_type=attrs['geo_type'].encode('utf-8'),
                url=attrs['url'].encode('utf-8'),
                pointer=attrs['pointer'].encode('utf-8'),
                sortorder=attrs['sortorder'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NyGeoPoint(NyAttributes, geopoint_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    icon = 'misc_/NaayaContent/NyGeoPoint.gif'
    icon_marked = 'misc_/NaayaContent/NyGeoPoint_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += geopoint_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, longitude, latitude, address, geo_type, url, pointer, contributor, releasedate, lang):
        """ """
        self.id = id
        geopoint_item.__dict__['__init__'](self, title, description, coverage, keywords, sortorder, longitude, latitude, address, geo_type, url, pointer, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

#    security.declarePrivate('objectkeywords')
#    def objectkeywords(self, lang):
#        return u' '.join([self._objectkeywords(lang), self.firstname, self.lastname, self.getLocalProperty('jobtitle', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'longitude="%s" latitude="%s" address="%s" geo_type="%s" url="%s" pointer="%s"' % \
            (self.utXmlEncode(self.longitude),
            self.utXmlEncode(self.latitude),
            self.utXmlEncode(self.address),
            self.utXmlEncode(self.geo_type),
            self.utXmlEncode(self.url),
            self.utXmlEncode(self.pointer))

#    security.declarePrivate('export_this_body_custom')
#    def export_this_body_custom(self):
#        r = []
#        ra = r.append
#        for l in self.gl_get_languages():
#            ra('<personaltitle lang="%s"><![CDATA[%s]]></personaltitle>' % (l, self.utToUtf8(self.getLocalProperty('personaltitle', l))))
#            ra('<jobtitle lang="%s"><![CDATA[%s]]></jobtitle>' % (l, self.utToUtf8(self.getLocalProperty('jobtitle', l))))
#        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='', sortorder='', approved='', 
        longitude='', latitude='', address='', geo_type='', url='', pointer='', releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, longitude, latitude, address, geo_type, url, pointer, releasedate, lang)
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self._local_properties_metadata = deepcopy(self.version._local_properties_metadata)
        self._local_properties = deepcopy(self.version._local_properties)
        self.sortorder = self.version.sortorder
        self.releasedate = self.version.releasedate
        self.longitude = self.version.longitude
        self.latitude = self.version.latitude
        self.address = self.version.address
        self.geo_type = self.version.geo_type
        self.url = self.version.url
        self.pointer = self.version.pointer
        self.setProperties(deepcopy(self.version.getProperties()))
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = geopoint_item(self.title, self.description, self.coverage, self.keywords, self.sortorder, self.longitude, self.latitude, self.address, self.geo_type, self.url, self.pointer, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='', 
        longitude='', latitude='', address='', geo_type='', url='', pointer='', releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, description=description, \
            coverage=coverage, keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
            longitude=longitude, latitude=latitude, address=address, geo_type=geo_type, url=url, pointer=pointer)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, longitude, latitude, address, geo_type, url, pointer, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, longitude, latitude, address, geo_type, url, pointer, releasedate, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, \
                    coverage=coverage, keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    longitude=longitude, latitude=latitude, address=address, geo_type=geo_type, url=url, pointer=pointer)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/geopoint_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'geopoint_index')

    security.declareProtected(view, 'marker_html')
    def marker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'marker_popup')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'geopoint_edit')

    #backwards compatibility
    security.declareProtected(view_management_screens, 'delete_obsolete_properties')
    def delete_obsolete_properties(self):
        """ """
        #to be removed
        try:
            del self.lon_cardinal
            del self.lon_ds
            del self.lon_ms
            del self.lon_ss
            del self.lat_cardinal
            del self.lat_ds
            del self.lat_ms
            del self.lat_ss
            self.longitude = 0.0
            self.latitude = 0.0
        except KeyError:
            pass

    security.declareProtected(view_management_screens, 'add_address')
    def add_address(self):
        """ add address """
        if not hasattr(self, 'address'):
            self.address = ''
            self._p_changed = 1

    security.declareProtected(view_management_screens, 'update_symbol_id')
    def update_symbol_id(self):
        """ not Valid XHTML 1.1 (id and name attributes must begin with a letter, not a digit) """
        #to be removed
        if not self.geo_type.startswith('symbol'):
            self.geo_type = 'symbol%s' % self.geo_type
            self._p_changed  = 1
            self.recatalogNyObject(self)

InitializeClass(NyGeoPoint)
