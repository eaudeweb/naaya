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
from Products.NaayaCore.GeoMapTool.managers.geo_utils import geo_utils

#module constants
METATYPE_OBJECT = 'Naaya GeoPoint'
LABEL_OBJECT = 'GeoPoint'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya GeoPoint objects'
OBJECT_FORMS = ['geopoint_add', 'geopoint_edit', 'geopoint_index']
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
    'lon_cardinal': (0, '', ''),
    'lon_ds':       (0, '', ''),
    'lon_ms':       (0, '', ''),
    'lon_ss':       (0, '', ''),
    'lat_cardinal': (0, '', ''),
    'lat_ds':       (0, '', ''),
    'lat_ms':       (0, '', ''),
    'lat_ss':       (0, '', ''),
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

def addNyGeoPoint(self, id='', title='', description='', coverage='', keywords='', sortorder='', lon_cardinal='', 
    lon_ds='', lon_ms='', lon_ss='', lat_cardinal='', lat_ds='', lat_ms='', lat_ss='', geo_type='', url='', pointer='',
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create an Contact type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'geopoint_manage_add' or l_referer.find('geopoint_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, lon_cardinal=lon_cardinal, lon_ds=lon_ds, lon_ms=lon_ms, \
            lon_ss=lon_ss, lat_cardinal=lat_cardinal, lat_ds=lat_ds, lat_ms=lat_ms, lat_ss=lat_ss, geo_type=geo_type, url=url, pointer=pointer)
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
        #verify if the object already exists
        try:
            ob = self._getOb(id)
            id = '%s-%s' % (id, self.utGenRandomId(5))
        except AttributeError:
            pass
        #create object
        ob = NyGeoPoint(id, title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, contributor, releasedate, lang)
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
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'geopoint_manage_add' or l_referer.find('geopoint_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'geopoint_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, coverage=coverage, \
                keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, lon_cardinal=lon_cardinal, \
                lon_ds=lon_ds, lon_ms=lon_ms, lon_ss=lon_ss, lat_cardinal=lat_cardinal, lat_ds=lat_ds, lat_ms=lat_ms, lat_ss=lat_ss, \
                geo_type=geo_type, url=url, pointer=pointer, lang=lang)
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
                lon_cardinal=attrs['lon_cardinal'].encode('utf-8'),
                lon_ds=attrs['lon_ds'].encode('utf-8'),
                lon_ms=attrs['lon_ms'].encode('utf-8'),
                lon_ss=attrs['lon_ss'].encode('utf-8'),
                lat_cardinal=attrs['lat_cardinal'].encode('utf-8'),
                lat_ds=attrs['lat_ds'].encode('utf-8'),
                lat_ms=attrs['lat_ms'].encode('utf-8'),
                lat_ss=attrs['lat_ss'].encode('utf-8'),
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

    def __init__(self, id, title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, contributor, releasedate, lang):
        """ """
        self.id = id
        geopoint_item.__dict__['__init__'](self, title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
                                            lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

#    security.declarePrivate('objectkeywords')
#    def objectkeywords(self, lang):
#        return u' '.join([self._objectkeywords(lang), self.firstname, self.lastname, self.getLocalProperty('jobtitle', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'lon_cardinal="%s", lon_ds="%s", lon_ms="%s", lon_ss="%s", lat_cardinal="%s", lat_ds="%s", lat_ms="%s", lat_ss="%s", geo_type="%s", url="%s", pointer="%s"' % \
            (self.utXmlEncode(self.lon_cardinal),
            self.utXmlEncode(self.lon_ds),
            self.utXmlEncode(self.lon_ms),
            self.utXmlEncode(self.lon_ss),
            self.utXmlEncode(self.lat_cardinal),
            self.utXmlEncode(self.lat_ds),
            self.utXmlEncode(self.lat_ms),
            self.utXmlEncode(self.lat_ss),
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
        lon_cardinal='', lon_ds='', lon_ms='', lon_ss='', lat_cardinal='', lat_ds='', lat_ms='', lat_ss='', 
        geo_type='', url='', pointer='', releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
                        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang)
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
        self.lon_cardinal = self.version.lon_cardinal
        self.lon_ds = self.version.lon_ds
        self.lon_ms = self.version.lon_ms
        self.lon_ss = self.version.lon_ss
        self.lat_cardinal = self.version.lat_cardinal
        self.lat_ds = self.version.lat_ds
        self.lat_ms = self.version.lat_ms
        self.lat_ss = self.version.lat_ss
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
        self.version = geopoint_item(self.title, self.description, self.coverage, self.keywords, self.sortorder, self.lon_cardinal, self.lon_ds, self.lon_ms, 
            self.lon_ss, self.lat_cardinal, self.lat_ds, self.lat_ms, self.lat_ss, self.geo_type, self.url, self.pointer, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='', 
        lon_cardinal='', lon_ds='', lon_ms='', lon_ss='', lat_cardinal='', lat_ds='', lat_ms='', 
        lat_ss='', geo_type='', url='', pointer='', releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, description=description, \
            coverage=coverage, keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
            lon_cardinal=lon_cardinal, lon_ds=lon_ds, lon_ms=lon_ms, lon_ss=lon_ss, lat_cardinal=lat_cardinal, \
            lat_ds=lat_ds, lat_ms=lat_ms, lat_ss=lat_ss, geo_type=geo_type, url=url, pointer=pointer)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
                                lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, lon_cardinal, lon_ds, lon_ms, 
                                        lon_ss, lat_cardinal, lat_ds, lat_ms, lat_ss, geo_type, url, pointer, releasedate, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, \
                    coverage=coverage, keywords=keywords, sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    lon_cardinal=lon_cardinal, lon_ds=lon_ds, lon_ms=lon_ms, lon_ss=lon_ss, lat_cardinal=lat_cardinal, \
                    lat_ds=lat_ds, lat_ms=lat_ms, lat_ss=lat_ss, geo_type=geo_type, url=url, pointer=pointer)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declarePrivate('exportGmlEntity')
    def exportGmlEntity(self):
        u = geo_utils()
        latdd = u.geoDMSToDd(self.lat_ds, self.lat_ms, self.lat_ss, self.lat_cardinal)
        londd = u.geoDMSToDd(self.lon_ds, self.lon_ms, self.lon_ss, self.lon_cardinal)
        lat, lon = u.geoDdToAzimuthalEquidistant(latdd, londd)
        return """
<gml:featureMember>
    <destinet fid="%s">
        <geometryProperty>
            <gml:Point>
                <gml:coordinates>%s,%s</gml:coordinates>
            </gml:Point>
        </geometryProperty>
        <fid>%s</fid>
        <latitude>%s</latitude>
        <longitude>%s</longitude>
        <X>%s</X>
        <Y>%s</Y>
        <lat>%s</lat>
        <lon>%s</lon>
        <identifier>%s</identifier>
        <title>%s</title>
        <url>%s</url>
        <symbol_id>%s</symbol_id>
        <symbol_label>%s</symbol_label>
    </destinet>
</gml:featureMember>
""" % (self.utXmlEncode(self.id),
        lat, lon, self.utXmlEncode(self.id),
        self.showLatitude(), self.showLongitude(), lon, lat,
        latdd, londd,
        self.utXmlEncode(self.absolute_url()),
        self.utXmlEncode(self.title_or_id()),
        self.utXmlEncode(self.url),
        self.utXmlEncode(self.geo_type),
        self.utXmlEncode(self.portal_map.getSymbolTitle(self.geo_type)))

    #api
    def showLongitude(self):
        #returns a string like DDMMSSC
        lon_ds, lon_ms, lon_ss = str(self.lon_ds), str(self.lon_ms), str(self.lon_ss)
        if len(lon_ds) == 1: lon_ds = '0%s' % lon_ds
        if len(lon_ms) == 1: lon_ms = '0%s' % lon_ms
        if len(lon_ss) == 1: lon_ss = '0%s' % lon_ss
        return '%s%s%s%s' % (lon_ds, lon_ms, lon_ss, self.lon_cardinal)

    def showLatitude(self):
        #returns a string like DDMMSSC
        lat_ds, lat_ms, lat_ss = str(self.lat_ds), str(self.lat_ms), str(self.lat_ss)
        if len(lat_ds) == 1: lat_ds = '0%s' % lat_ds
        if len(lat_ms) == 1: lat_ms = '0%s' % lat_ms
        if len(lat_ss) == 1: lat_ss = '0%s' % lat_ss
        return '%s%s%s%s' % (lat_ds, lat_ms, lat_ss, self.lat_cardinal)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/geopoint_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'geopoint_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'geopoint_edit')

InitializeClass(NyGeoPoint)