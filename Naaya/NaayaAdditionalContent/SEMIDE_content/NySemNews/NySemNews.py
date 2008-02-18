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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from copy import deepcopy

#Zope imports
from Globals        import InitializeClass
from AccessControl  import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile

#Product imports
from Products.NaayaContent.constants    import *
from Products.NaayaBase.constants       import *
from Products.NaayaBase.NyItem          import NyItem
from Products.NaayaBase.NyAttributes    import NyAttributes
from Products.NaayaBase.NyCheckControl  import NyCheckControl
from semnews_item                       import semnews_item

#pluggable type metadata
METATYPE_OBJECT = 'Naaya Semide News'
LABEL_OBJECT = 'News'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide News objects'
OBJECT_FORMS = ['semnews_add', 'semnews_edit', 'semnews_index']
OBJECT_CONSTRUCTORS = ['manage_addNySemNews_html', 'semnews_add_html', 'addNySemNews', 'importNySemNews']
OBJECT_ADD_FORM = 'semnews_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide News type.'
PREFIX_OBJECT = 'snews'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (1, MUST_BE_NONEMPTY, 'The Geographical coverage field must have a value.'),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'creator':          (0, '', ''),
    'creator_email':    (0, '', ''),
    'contact_person':   (0, '', ''),
    'contact_email':    (0, '', ''),
    'contact_phone':    (0, '', ''),
    'rights':           (0, '', ''),
    'news_type':        (0, '', ''),
    'file_link':        (0, '', ''),
    'file_link_local':  (0, '', ''),
    'source':           (0, '', ''),
    'source_link':      (0, '', ''),
    'subject':          (0, '', ''),
    'relation':         (0, '', ''),
    'news_date':        (1, MUST_BE_DATETIME_STRICT, 'The News date field must contain a valid date.'),
    'working_langs':    (0, '', ''),
    'lang':             (0, '', ''),
    'file':             (0, '', ''),
}

manage_addNySemNews_html = PageTemplateFile('zpt/semnews_manage_add', globals())
manage_addNySemNews_html.kind = METATYPE_OBJECT
manage_addNySemNews_html.action = 'addNySemNews'

def semnews_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemNews'}, 'semnews_add')

def addNySemNews(self, id='', creator='', creator_email='', contact_person='', contact_email='',
    contact_phone='', rights='', title='', news_type='', file_link='', file_link_local='', source='',
    source_link='', keywords='', description='', subject='', relation='', coverage='', news_date='',
    working_langs='', sortorder='', contributor=None, releasedate='', discussion='', lang=None, file=None,
    REQUEST=None, **kwargs):
    """
    Create a News type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'semnews_manage_add' or l_referer.find('semnews_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, creator=creator, creator_email=creator_email, \
            contact_person=contact_person, contact_email=contact_email, contact_phone=contact_phone, \
            rights=rights, news_type=news_type, file_link=file_link, file_link_local=file_link_local, \
            source=source, source_link=source_link, subject=subject, relation=relation, news_date=news_date, \
            working_langs=working_langs)
    else:
        r = []
    if not len(r):
        #process parameters
        news_date = self.utConvertStringToDateTimeObj(news_date)
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NySemNews(id, creator, creator_email, contact_person, contact_email,
            contact_phone, rights, title, news_type, file_link, file_link_local, 
            source, source_link, keywords, description, subject, relation, coverage, news_date,
            working_langs, sortorder, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.approveThis(approved, approved_by)
        ob.handleUpload(file)
        ob.submitThis()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'semnews_manage_add' or l_referer.find('semnews_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'semnews_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                creator=creator, creator_email=creator_email, \
                contact_person=contact_person, contact_email=contact_email, contact_phone=contact_phone, \
                rights=rights, news_type=news_type, file_link=file_link, file_link_local=file_link_local, \
                source=source, source_link=source_link, subject=subject, relation=relation, news_date=news_date, \
                working_langs=working_langs, lang=lang)
            REQUEST.RESPONSE.redirect('%s/semnews_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNySemNews(self, param, id, attrs, content, properties, discussion, objects):
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
            addNySemNews(self, id=id,
                creator         = attrs['creator'].encode('utf-8'),
                creator_email   = attrs['creator_email'].encode('utf-8'),
                news_type       = attrs['news_type'].encode('utf-8'),
                source_link     = attrs['source_link'].encode('utf-8'),
                subject         = eval(attrs['subject'].encode('utf-8')),
                relation        = attrs['relation'].encode('utf-8'),
                news_date       = attrs['news_date'].encode('utf-8'),
                working_langs   = eval(attrs['working_langs'].encode('utf-8')),
                contributor     = self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                sortorder       = attrs['sortorder'].encode('utf-8'),
                discussion      = abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            if objects:
                obj = objects[0]
                data=self.utBase64Decode(obj.attrs['file'].encode('utf-8'))
                ctype = obj.attrs['content_type'].encode('utf-8')
                try:
                    size = int(obj.attrs['size'])
                except TypeError, ValueError:
                    size = 0
                name = obj.attrs['name'].encode('utf-8')
                ob.update_data(data, ctype, size, name)
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NySemNews(NyAttributes, semnews_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemNews.gif'
    icon_marked = 'misc_/NaayaContent/NySemNews_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += semnews_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, creator, creator_email, contact_person, contact_email,
        contact_phone, rights, title, news_type, file_link, file_link_local, 
        source, source_link, keywords, description, subject, relation, coverage, news_date,
        working_langs, sortorder, contributor, releasedate, lang, file=None):
        """ """
        self.id = id
        semnews_item.__dict__['__init__'](self, creator, creator_email, contact_person, contact_email,
            contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
            keywords, description, subject, relation, coverage, news_date, working_langs, sortorder,
            releasedate, lang, file)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'resource_type')
    def resource_type(self):
        return self.news_type

    security.declareProtected(view, 'resource_date')
    def resource_date(self):
        return self.news_date

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(self.subject)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('source', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'creator="%s" creator_email="%s" news_type="%s" \
                source_link="%s" subject="%s" relation="%s" news_date="%s" working_langs="%s"' % \
            (self.utXmlEncode(self.creator),
                self.utXmlEncode(self.creator_email),
                self.utXmlEncode(self.news_type),
                self.utXmlEncode(self.source_link),
                self.utXmlEncode(self.subject),
                self.utXmlEncode(self.relation),
                self.utXmlEncode(self.news_date),
                self.utXmlEncode(self.working_langs))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<contact_person lang="%s"><![CDATA[%s]]></contact_person>' % (l, self.utToUtf8(self.getLocalProperty('contact_person', l))))
            ra('<contact_email lang="%s"><![CDATA[%s]]></contact_email>' % (l, self.utToUtf8(self.getLocalProperty('contact_email', l))))
            ra('<contact_phone lang="%s"><![CDATA[%s]]></contact_phone>' % (l, self.utToUtf8(self.getLocalProperty('contact_phone', l))))
            ra('<rights lang="%s"><![CDATA[%s]]></rights>' % (l, self.utToUtf8(self.getLocalProperty('rights', l))))
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
            ra('<file_link lang="%s"><![CDATA[%s]]></file_link>' % (l, self.utToUtf8(self.getLocalProperty('file_link', l))))
            ra('<file_link_local lang="%s"><![CDATA[%s]]></file_link_local>' % (l, self.utToUtf8(self.getLocalProperty('file_link_local', l))))
        ra('<item file="%s" content_type="%s" size="%s" name="%s"/>' % (
            self.utBase64Encode(str(self.utNoneToEmpty(self.get_data()))),
            self.utXmlEncode(self.getContentType()),
            self.getSize(),
            self.downloadfilename())
        )
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
        ra('<dc:format>%s</dc:format>' % self.utXmlEncode(self.format()))
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(self.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:relation>%s</dc:relation>' % self.utXmlEncode(self.relation))
        for k in self.subject:
            if k:
                theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
                theme_name = theme_ob.theme_name
                if theme_name:
                    ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(theme_name.strip()))

        for k in self.getLocalProperty('keywords', lang).split(','):
            ra('<ut:keywords>%s</ut:keywords>' % self.utXmlEncode(k))
        ra('<ut:creator_mail>%s</ut:creator_mail>' % self.utXmlEncode(self.creator_email))
        ra('<ut:contact_name>%s</ut:contact_name>' % self.utXmlEncode(self.getLocalProperty('contact_person', lang)))
        ra('<ut:contact_mail>%s</ut:contact_mail>' % self.utXmlEncode(self.getLocalProperty('contact_email', lang)))
        ra('<ut:contact_phone>%s</ut:contact_phone>' % self.utXmlEncode(self.getLocalProperty('contact_phone', lang)))
        ra('<ut:news_type>%s</ut:news_type>' % self.utXmlEncode(self.news_type))
        ra('<ut:file_link>%s</ut:file_link>' % self.utXmlEncode(self.getLocalProperty('file_link', lang)))
        ra('<ut:file_link_local>%s</ut:file_link_local>' % self.utXmlEncode(self.getLocalProperty('file_link_local', lang)))
        ra('<ut:source_link>%s</ut:source_link>' % self.utXmlEncode(self.source_link))
        ra('<ut:start_date>%s</ut:start_date>' % self.utShowFullDateTimeHTML(self.news_date))
        ra('<ut:save_date>%s</ut:save_date>' % self.utShowFullDateTimeHTML(self.bobobase_modification_time()))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    def manage_FTPget(self):
        """ Return body for ftp """
        return self.description


    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, creator='', creator_email='', contact_person='', contact_email='',
        contact_phone='', rights='', title='', news_type='', file_link='', file_link_local='',
        source='', source_link='', keywords='', description='', subject=[], relation='', coverage='',
        news_date='', working_langs=[], sortorder='', approved='', releasedate='', discussion='',
        lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        working_langs = self.utConvertToList(working_langs)
        subject = self.utConvertToList(subject)
        news_date = self.utConvertStringToDateTimeObj(news_date)
        if approved: approved = 1
        else: approved = 0
        if not lang: lang = self.gl_get_selected_language()
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        self.save_properties(creator, creator_email, contact_person, contact_email,
            contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
            keywords, description, subject, relation, coverage, news_date, working_langs, sortorder,
            releasedate, lang)
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
        self.creator =          self.version.creator
        self.creator_email =    self.version.creator_email
        self.news_type =        self.version.news_type
        self.file_link =        self.version.file_link
        self.file_link_local =  self.version.file_link_local
        self.source_link =      self.version.source_link
        self.subject =          self.version.subject
        self.relation =         self.version.relation
        self.news_date =        self.version.news_date
        self.working_langs =    self.version.working_langs
        self.sortorder =        self.version.sortorder
        self.releasedate =      self.version.releasedate
        self.update_data(self.version.get_data(as_string=False),
                         self.version.getContentType(), self.version.get_size(),
                         self.downloadfilename(version=True))
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
        self.version = semnews_item(self.creator, self.creator_email, self.contact_person,
            self.contact_email, self.contact_phone, self.rights, self.title, self.news_type,
            self.file_link, self.file_link_local, self.source, self.source_link, self.keywords,
            self.description, self.subject, self.relation, self.coverage, self.news_date,
            self.working_langs, self.sortorder, self.releasedate, self.gl_get_selected_language(), self.get_data(as_string=False))
        self.version.update_data(self.get_data(), self.getContentType(), self.get_size(), self.downloadfilename())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, creator='', creator_email='', contact_person='', contact_email='', contact_phone='', rights='',
        title='', news_type='', file_link='', file_link_local='', source='', source_link='', keywords='', description='', subject=[],
        relation='', coverage='', news_date='', working_langs=[], sortorder='', releasedate='', discussion='', lang=None,
        REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        working_langs = self.utConvertToList(working_langs)
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            creator=creator, creator_email=creator_email, \
            contact_person=contact_person, contact_email=contact_email, contact_phone=contact_phone, \
            rights=rights, news_type=news_type, file_link=file_link, file_link_local=file_link_local, \
            source=source, source_link=source_link, subject=subject, relation=relation, news_date=news_date, \
            working_langs=working_langs)
        # If errors raise
        if len(r):
            if not REQUEST:
                raise Exception, '%s' % ', '.join(r)
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                creator=creator, creator_email=creator_email, \
                contact_person=contact_person, contact_email=contact_email, contact_phone=contact_phone, \
                rights=rights, news_type=news_type, file_link=file_link, file_link_local=file_link_local, \
                source=source, source_link=source_link, subject=subject, relation=relation, news_date=news_date, \
                working_langs=working_langs)
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            return
        #
        # Save properties
        #
        # Upload file
        file_form = dict([(key, value) for key, value in kwargs.items()])
        if REQUEST:
            file_form.update(REQUEST.form)
        file_source = file_form.get('file_source', None)
        if file_source:
            attached_file = file_form.get('file', '')
            context = self
            if self.hasVersion():
                context = self.version
            context.handleUpload(attached_file)
        # Update properties
        news_date = self.utConvertStringToDateTimeObj(news_date)
        sortorder = int(sortorder)
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            releasedate = self.process_releasedate(releasedate, self.releasedate)
            self.save_properties(creator, creator_email, contact_person, contact_email,
                contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
                keywords, description, subject, relation, coverage, news_date, working_langs, sortorder,
                releasedate, lang)
            self.updatePropertiesFromGlossary(lang)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            releasedate = self.process_releasedate(releasedate, self.version.releasedate)
            self.version.save_properties(creator, creator_email, contact_person, contact_email,
                contact_phone, rights, title, news_type, file_link, file_link_local, source, source_link,
                keywords, description, subject, relation, coverage, news_date, working_langs, sortorder,
                releasedate, lang)
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

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semnews_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semnews_index')

    security.declareProtected(view, 'picture_html')
    def picture_html(self, REQUEST=None, RESPONSE=None):
        """ """
        REQUEST.RESPONSE.setHeader('content-type', 'text/html')
        return '<img src="getBigPicture" border="0" alt="" />'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semnews_edit')
    
    security.declarePublic('downloadfilename')
    def downloadfilename(self, version=False):
        """ """
        context = self
        if version and self.hasVersion():
            context = self.version
        attached_file = context.get_data(as_string=False)
        filename = getattr(attached_file, 'filename', [])
        if not filename:
            return self.title_or_id()
        return filename[-1]
        
    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        version = REQUEST.get('version', False)
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Content-Length', self.getSize())
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.downloadfilename(version=version))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        if version and self.hasVersion():
            return semnews_item.index_html(self.version, REQUEST, RESPONSE)
        return semnews_item.index_html(self, REQUEST, RESPONSE)

    security.declarePublic('getDownloadUrl')
    def getDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)
    
    security.declarePublic('getEditDownloadUrl')
    def getEditDownloadUrl(self):
        """ """
        site = self.getSite()
        file_path = self._get_data_name()
        media_server = getattr(site, 'media_server', '').strip()
        if not (media_server and file_path):
            return self.absolute_url() + '/download?version=1'
        file_path = (media_server,) + tuple(file_path)
        return '/'.join(file_path)

InitializeClass(NySemNews)
