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
from project_item import project_item

#pluggable type metadata
METATYPE_OBJECT = 'Naaya SMAP Project'
LABEL_OBJECT = 'Project'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya SMAP Project objects'
OBJECT_FORMS = ['project_add', 'project_edit', 'project_index']
OBJECT_CONSTRUCTORS = ['manage_addNySMAPProject_html', 'project_add_html', 'addNySMAPProject', 'importNySMAPProject']
OBJECT_ADD_FORM = 'project_add_html'
DESCRIPTION_OBJECT = 'This is Naaya SMAP Project type.'
PREFIX_OBJECT = 'prj'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'country':      (0, '', ''),
    'contact':      (0, '', ''),
    'donor':        (0, '', ''),
    'links':        (0, '', ''),
    'organisation': (0, '', ''),
    'location':     (0, '', ''),
    'main_issues':  (0, '', ''),
    'tools':        (0, '', ''),
    'budget':       (0, '', ''),
    'timeframe':    (0, '', ''),
    'priority_area':(0, '', ''),
    'focus':        (0, '', ''),
    'lang':         (0, '', '')
}

manage_addNySMAPProject_html = PageTemplateFile('zpt/project_manage_add', globals())
manage_addNySMAPProject_html.kind = METATYPE_OBJECT
manage_addNySMAPProject_html.action = 'addNySMAPProject'

def project_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySMAPProject'}, 'project_add')

def addNySMAPProject(self, id='', title='', description='', coverage='', keywords='', country='', sortorder='', 
                    contact='', donor='', links='', organisation='', location='', main_issues='', tools='', budget='',
                    timeframe='', focus='', contributor=None, releasedate='', discussion='',
                    lang=None, REQUEST=None, **kwargs):
    """
    Create a Project type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(6)
    try: sortorder =    abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'project_manage_add' or l_referer.find('project_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title,
            description=description, coverage=coverage, keywords=keywords, country=country, sortorder=sortorder,
            releasedate=releasedate, discussion=discussion, contact=contact, donor=donor, links=links,
            organisation=organisation, location=location, main_issues=main_issues, tools=tools, budget=budget,
            timeframe=timeframe, focus=focus)
    else:
        r = []
    if not len(r):
        #process parameters
        if lang is None: lang = self.gl_get_selected_language()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        releasedate = self.process_releasedate(releasedate)
        country = self.utConvertToList(country)
        focus = self.utConvertToList(focus)
        res = {}
        for x in focus:
            res[x.split('|@|')[0]] = ''
        priority_area = res.keys()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NySMAPProject(id, title, description, coverage, keywords, country, contact, donor, links, organisation,
                    location, main_issues, tools, budget, timeframe, priority_area, focus, sortorder, 
                    contributor, releasedate, lang)
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
            if l_referer == 'project_manage_add' or l_referer.find('project_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'project_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description,
                    coverage=coverage, keywords=keywords, country=country, sortorder=sortorder, releasedate=releasedate,
                    discussion=discussion, contact=contact, donor=donor, links=links, organisation=organisation,
                    location=location, main_issues=main_issues, tools=tools, budget=budget, timeframe=timeframe,
                    focus=focus, lang=lang)
            REQUEST.RESPONSE.redirect('%s/project_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNySMAPProject(self, param, id, attrs, content, properties, discussion, objects):
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
            addNySMAPProject(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                main_issues=attrs['main_issues'].encode('utf-8'),
                country=eval(attrs['country'].encode('utf-8')),
                tools=attrs['tools'].encode('utf-8'),
                budget=attrs['budget'].encode('utf-8'),
                timeframe=attrs['timeframe'].encode('utf-8'),
                priority_area=attrs['priority_area'].encode('utf-8'),
                focus=eval(attrs['focus'].encode('utf-8')),
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

class NySMAPProject(NyAttributes, project_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySMAPProject.gif'
    icon_marked = 'misc_/NaayaContent/NySMAPProject_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += project_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, country, contact,
        donor, links, organisation, location, main_issues, tools, budget,
        timeframe, priority_area, focus, sortorder, contributor, releasedate, lang):
        """ """
        self.id = id
        project_item.__dict__['__init__'](self, title, description, coverage, keywords, country, contact,
                                            donor, links, organisation, location, main_issues, tools, budget,
                                            timeframe, priority_area, focus, sortorder, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('donor', lang),
                        self.getLocalProperty('organisation', lang), self.getLocalProperty('contact', lang),
                        self.getLocalProperty('location', lang)])

    security.declareProtected(view, 'resource_area_exp')
    def resource_area(self):
        return self.priority_area

    security.declareProtected(view, 'resource_focus_exp')
    def resource_focus(self):
        return ' '.join(self.focus)

    security.declareProtected(view, 'resource_country')
    def resource_country(self):
        return ' '.join(self.country)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'priority_area="%s" budget="%s" timeframe="%s" focus="%s" main_issues="%s" tools="%s" country="%s"'% \
            (self.utXmlEncode(self.priority_area),
                self.utXmlEncode(self.budget),
                self.utXmlEncode(self.utNoneToEmpty(self.timeframe)),
                self.utXmlEncode(self.focus),
                self.utXmlEncode(self.main_issues),
                self.utXmlEncode(self.tools),
                self.utXmlEncode(self.country))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<donor lang="%s"><![CDATA[%s]]></donor>' % (l, self.utToUtf8(self.getLocalProperty('donor', l))))
            ra('<contact lang="%s"><![CDATA[%s]]></contact>' % (l, self.utToUtf8(self.getLocalProperty('contact', l))))
            ra('<organisation lang="%s"><![CDATA[%s]]></organisation>' % (l, self.utToUtf8(self.getLocalProperty('organisation', l))))
            ra('<location lang="%s"><![CDATA[%s]]></location>' % (l, self.utToUtf8(self.getLocalProperty('location', l))))
            ra('<links lang="%s"><![CDATA[%s]]></links>' % (l, self.utToUtf8(self.getLocalProperty('links', l))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>text</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='', country='', contact='', donor='', links='',
                        organisation='', location='', main_issues='', tools='', budget='', timeframe='', focus='', sortorder='', 
                        approved='', releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        if not lang: lang = self.gl_get_selected_language()
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        country = self.utConvertToList(country)
        focus = self.utConvertToList(focus)
        res = {}
        for x in focus:
            res[x.split('|@|')[0]] = ''
        priority_area = res.keys()
        self.save_properties(title, description, coverage, keywords, country, contact, donor, links, organisation,
                            location, main_issues, tools, budget, timeframe, priority_area, focus,
                            sortorder, releasedate, lang)
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
        self.country = self.version.country
        self.contact = self.version.contact
        self.donor = self.version.donor
        self.links = self.version.links
        self.organisation = self.version.organisation
        self.location = self.version.location
        self.main_issues = self.version.main_issues
        self.tools = self.version.tools
        self.budget = self.version.budget
        self.timeframe = self.version.timeframe
        self.priority_area = self.version.priority_area
        self.focus = self.version.focus
        self.sortorder = self.version.sortorder
        self.releasedate = self.version.releasedate
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
        self.version = project_item(self.title, self.description, self.coverage, self.keywords, self.country, self.contact,
                        self.donor, self.links, self.organisation, self.location, self.main_issues, self.tools,
                        self.budget, self.timeframe, self.priority_area, self.focus, self.sortorder, self.releasedate,
                        self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', country='', contact='', donor='',
                links='', organisation='', location='', main_issues='', tools='', budget='', timeframe='',
                focus='', sortorder='', releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        country = self.utConvertToList(country)
        focus = self.utConvertToList(focus)
        res = {}
        for x in focus:
            res[x.split('|@|')[0]] = ''
        priority_area = res.keys()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, country=country, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, contact=contact, donor=donor, links=links,
            organisation=organisation, location=location, main_issues=main_issues, tools=tools, budget=budget,
            timeframe=timeframe, focus=focus)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, country, contact, donor, links, organisation,
                                     location, main_issues, tools, budget, timeframe, priority_area, focus,
                                     sortorder, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, country, contact, donor, 
                                    links, organisation, location, main_issues, tools, budget, timeframe, 
                                    priority_area, focus, sortorder, releasedate, lang)
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
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description,
                    coverage=coverage, keywords=keywords, country=country, sortorder=sortorder, releasedate=releasedate,
                    discussion=discussion, contact=contact, donor=donor, links=links, organisation=organisation,
                    location=location, main_issues=main_issues, tools=tools, budget=budget, timeframe=timeframe,
                    priority_area=priority_area, focus=focus)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'checkFocus')
    def checkFocus(self, priority_area, focus_id):
        """ """
        for f in self.focus:
            if f == '%s|@|%s' % (priority_area, focus_id):
                return True
        return False

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/project_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'project_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'project_edit')

InitializeClass(NySMAPProject)