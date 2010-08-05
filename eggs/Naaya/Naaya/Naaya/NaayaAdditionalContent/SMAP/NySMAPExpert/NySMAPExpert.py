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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports
from copy import deepcopy

#Zope imports
from OFS.Image import File, cookId
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
from Products.NaayaBase.NyVersioning import NyVersioning
from expert_item import expert_item

#module constants
METATYPE_OBJECT = 'Naaya SMAP Expert'
LABEL_OBJECT = 'Expert'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya SMAP Expert objects'
OBJECT_FORMS = ['expert_add', 'expert_edit', 'expert_index']
OBJECT_CONSTRUCTORS = ['manage_addNySMAPExpert_html', 'expert_add_html', 'addNySMAPExpert', 'importNySMAPExpert']
OBJECT_ADD_FORM = 'expert_add_html'
DESCRIPTION_OBJECT = 'This is Naaya SMAP Expert type.'
PREFIX_OBJECT = 'expert'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (0, '', ''),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'surname':          (1, MUST_BE_NONEMPTY, 'The Surname field must have a value.'),
    'name':             (1, MUST_BE_NONEMPTY, 'The Name field must have a value.'),
    'ref_lang':         (0, '', ''),
    'country':          (0, '', ''),
    'maintopics':       (0, '', ''),
    'subtopics':        (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'file':             (0, '', ''),
    'downloadfilename': (0, '', ''),
    'content_type':     (0, '', ''),
    'email':            (0, '', ''),
    'lang':             (0, '', '')
}

manage_addNySMAPExpert_html = PageTemplateFile('zpt/expert_manage_add', globals())
manage_addNySMAPExpert_html.kind = METATYPE_OBJECT
manage_addNySMAPExpert_html.action = 'addNySMAPExpert'

def expert_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySMAPExpert'}, 'expert_add')

def addNySMAPExpert(self, id='', title='', description='', coverage='', keywords='', surname='', 
        name='', ref_lang='', country='', subtopics='', sortorder='',
        file='', precondition='', content_type='', downloadfilename='', email='',
        contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Expert type of object.
    """
    #process parameters
    if downloadfilename == '': downloadfilename = cookId('', title, file)[0]
    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'expert_manage_add' or l_referer.find('expert_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, 
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, 
            surname=surname, name=name, ref_lang=ref_lang, country=country, 
            subtopics=subtopics, releasedate=releasedate, discussion=discussion, file=file, 
            downloadfilename=downloadfilename, email=email)
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
        subtopics = self.utConvertToList(subtopics)
        res = {}
        for x in subtopics:
            res[x.split('|@|')[0]] = ''
        maintopics = res.keys()
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NySMAPExpert(id, title, description, coverage, keywords, surname, name, ref_lang, country, 
                    maintopics, subtopics, sortorder, '', precondition, content_type, downloadfilename, 
                    email, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.submitThis()
        ob.approveThis(approved, approved_by)
        ob.handleUpload(file)
        #ob.createVersion(self.REQUEST.AUTHENTICATED_USER.getUserName())
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'expert_manage_add' or l_referer.find('expert_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'expert_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, 
                        coverage=coverage, keywords=keywords, sortorder=sortorder, surname=surname, 
                        name=name, ref_lang=ref_lang, country=country, subtopics=subtopics, releasedate=releasedate, 
                        discussion=discussion, downloadfilename=downloadfilename, email=email)
            REQUEST.RESPONSE.redirect('%s/expert_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNySMAPExpert(self, param, id, attrs, content, properties, discussion, objects):
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
            addNySMAPExpert(self, id=id,
                surname=attrs['surname'].encode('utf-8'),
                name=attrs['name'].encode('utf-8'),
                ref_lang=attrs['ref_lang'].encode('utf-8'),
                country=attrs['country'].encode('utf-8'),
                maintopics=attrs['maintopics'].encode('utf-8'),
                subtopics=eval(attrs['subtopics'].encode('utf-8')),
                email=attrs['email'].encode('utf-8'),
                sortorder=attrs['sortorder'].encode('utf-8'),
                source='file', file=self.utBase64Decode(attrs['file'].encode('utf-8')),
                downloadfilename=attrs['downloadfilename'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            #set the real content_type and precondition
            ob.content_type = attrs['content_type'].encode('utf-8')
            ob.precondition = attrs['precondition'].encode('utf-8')
            ob._p_changed = 1
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NySMAPExpert(NyAttributes, expert_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySMAPExpert.gif'
    icon_marked = 'misc_/NaayaContent/NySMAPExpert_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += expert_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        #l_options += NyVersioning.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, surname, name, ref_lang, country, 
                    maintopics, subtopics, sortorder, file, precondition, content_type, downloadfilename, 
                    email, contributor, releasedate, lang):
        """ """
        self.id = id
        expert_item.__dict__['__init__'](self, id, title, description, coverage, keywords, surname, name, 
            ref_lang, country, maintopics, subtopics, sortorder, file, precondition, content_type, 
            downloadfilename, email, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.surname, self.name])

    security.declareProtected(view, 'resource_area_exp')
    def resource_area_exp(self):
        return self.maintopics

    security.declareProtected(view, 'resource_focus_exp')
    def resource_focus_exp(self):
        return ' '.join(self.subtopics)

    security.declareProtected(view, 'resource_country')
    def resource_country(self):
        return self.country

    #override handlers
    def manage_afterAdd(self, item, container):
        """
        This method is called, whenever _setObject in ObjectManager gets called.
        """
        NySMAPExpert.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.catalogNyObject(self)

    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        NySMAPExpert.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.uncatalogNyObject(self)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'surname="%s" name="%s" ref_lang="%s" country="%s" maintopics="%s" subtopics="%s" email="%s" downloadfilename="%s" file="%s" content_type="%s" precondition="%s"' % \
            (self.utXmlEncode(self.surname),
                self.utXmlEncode(self.name),
                self.utXmlEncode(self.ref_lang),
                self.utXmlEncode(self.country),
                self.utXmlEncode(self.maintopics),
                self.utXmlEncode(self.subtopics),
                self.utXmlEncode(self.email),
                self.utXmlEncode(self.downloadfilename),
                self.utBase64Encode(str(self.utNoneToEmpty(self.data))),
                self.utXmlEncode(self.content_type),
                self.utXmlEncode(self.precondition))

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        r = []
        ra = r.append
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>application</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='', surname='', 
        name='', ref_lang='', country='', subtopics='', sortorder='',
        file='', precondition='', content_type='', downloadfilename='', email='', approved=None,
        contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        subtopics = self.utConvertToList(subtopics)
        res = {}
        for x in subtopics:
            res[x.split('|@|')[0]] = ''
        maintopics = res.keys()
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, surname, name, ref_lang, country, 
            maintopics, subtopics, sortorder, downloadfilename, email, releasedate, lang)
        self.content_type = content_type
        self.precondition = precondition
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

    security.declareProtected(view_management_screens, 'manageUpload')
    def manageUpload(self, file='', REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        self.downloadfilename = self.handleUpload(file)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_upload')
    def manage_upload(self):
        """ """
        raise EXCEPTION_NOTACCESIBLE, 'manage_upload'

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
        self.surname = self.version.surname
        self.name = self.version.name
        self.ref_lang = self.version.ref_lang
        self.country = self.version.country
        self.maintopics = self.version.maintopics
        self.subtopics = self.version.subtopics
        self.email = self.version.email
        self.sortorder = self.version.sortorder
        self.downloadfilename = self.version.downloadfilename
        self.update_data(self.version.data, self.version.content_type)
        self.content_type = self.version.content_type
        self.precondition = self.version.precondition
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
        self.checkout = 0
        self.checkout_user = None
        #self.version = None
        #self.createVersion(self.REQUEST.AUTHENTICATED_USER.getUserName())
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
        self.version = expert_item(self.id, self.title, self.description, self.coverage, self.keywords, self.surname, 
            self.name, self.ref_lang, self.country, self.maintopics, self.subtopics, self.sortorder, 
            self.data, self.precondition, self.content_type, self.downloadfilename, self.email, self.releasedate, 
            self.gl_get_selected_language())
        self.version.update_data(self.data, self.content_type)
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', surname='', 
        name='', ref_lang='', country='', subtopics='', sortorder='',
        precondition='', content_type='', downloadfilename='', email='',
        releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        subtopics = self.utConvertToList(subtopics)
        res = {}
        for x in subtopics:
            res[x.split('|@|')[0]] = ''
        maintopics = res.keys()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, 
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, 
            surname=surname, name=name, ref_lang=ref_lang, country=country, maintopics=maintopics, 
            subtopics=subtopics, releasedate=releasedate, discussion=discussion, downloadfilename=downloadfilename, email=email)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, surname, name, ref_lang, country, 
            maintopics, subtopics, sortorder, downloadfilename, email, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.content_type = content_type
                self.precondition = precondition
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, surname, name, ref_lang, country, 
            maintopics, subtopics, sortorder, downloadfilename, email, releasedate, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.content_type = content_type
                self.version.precondition = precondition
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
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, 
                        description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, 
                        surname=surname, name=name, ref_lang=ref_lang, country=country, maintopics=maintopics, 
                        subtopics=subtopics, releasedate=releasedate, discussion=discussion, downloadfilename=downloadfilename, email=email)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, file='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            self.downloadfilename = self.handleUpload(file)
            #if version: self.createVersion(self.REQUEST.AUTHENTICATED_USER.getUserName())
        else:
            #this object has been checked out; save changes into the version object
            if self. checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            self.version.downloadfilename = self.version.handleUpload(file)
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/expert_manage_edit', globals())

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_edit')

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', self.ut_content_disposition(self.downloadfilename))
        return expert_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        return expert_item.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

InitializeClass(NySMAPExpert)