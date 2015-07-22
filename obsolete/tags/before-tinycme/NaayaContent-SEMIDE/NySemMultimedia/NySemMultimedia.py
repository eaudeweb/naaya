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
from semmultimedia_item                 import semmultimedia_item

#module constants
METATYPE_OBJECT = 'Naaya Semide Multimedia'
LABEL_OBJECT = 'Multimedia'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Multimedia objects'
OBJECT_FORMS = ['semmultimedia_add', 'semmultimedia_edit', 'semmultimedia_index']
OBJECT_CONSTRUCTORS = ['manage_addNySemMultimedia_html', 'semmultimedia_add_html', 'addNySemMultimedia', 'importNySemMultimedia']
OBJECT_ADD_FORM = 'semmultimedia_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide Multimedia type.'
PREFIX_OBJECT = 'sml'
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'creator':          (0, '', ''),
    'creator_email':    (0, '', ''),
    'rights':           (0, '', ''),
    'type_multimedia':  (0, '', ''),
    'source':           (1, MUST_BE_NONEMPTY, 'The Source field must have a value.'),
    'source_link':      (0, '', ''),
    'subject':          (0, '', ''),
    'relation':         (0, '', ''),
    'file_link':        (0, '', ''),
    'file_link_local':  (0, '', ''),
    'format':           (0, '', ''),
    'lang':             (0, '', '')
}

manage_addNySemMultimedia_html = PageTemplateFile('zpt/semmultimedia_manage_add', globals())
manage_addNySemMultimedia_html.kind = METATYPE_OBJECT
manage_addNySemMultimedia_html.action = 'addNySemMultimedia'

def semmultimedia_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemMultimedia'}, 'semmultimedia_add')

def addNySemMultimedia(self, id='', title='', description='', coverage='', keywords='', sortorder='', creator='', 
    creator_email='', rights='', type_multimedia='', source='', source_link='', subject='', relation='', 
    file_link='', file_link_local='', format='', discussion='', contributor=None, releasedate='',
    lang=None, REQUEST=None, **kwargs):
    """
    Create an Text Laws type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'semmultimedia_manage_add' or l_referer.find('semmultimedia_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            creator=creator, creator_email=creator_email, rights=rights, type_multimedia=type_multimedia, \
            source=source, source_link=source_link, subject=subject, relation=relation, \
            file_link=file_link, file_link_local=file_link_local, format=format)
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
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #create object
        ob = NySemMultimedia(id, title, description, coverage, keywords, sortorder, creator, creator_email, 
            rights, type_multimedia, source, source_link, subject, relation, file_link, 
            file_link_local, format, contributor, releasedate, lang)
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
            if l_referer == 'semmultimedia_manage_add' or l_referer.find('semmultimedia_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'semmultimedia_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                creator=creator, creator_email=creator_email, rights=rights, type_multimedia=type_multimedia, \
                source=source, source_link=source_link, subject=subject, relation=relation, \
                file_link=file_link, file_link_local=file_link_local, format=format)
            REQUEST.RESPONSE.redirect('%s/semmultimedia_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNySemMultimedia(self, param, id, attrs, content, properties, discussion, objects):
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
            addNySemMultimedia(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                creator_email=attrs['creator_email'].encode('utf-8'),
                type_multimedia=attrs['type_multimedia'].encode('utf-8'),
                source_link=attrs['source_link'].encode('utf-8'),
                subject=eval(attrs['subject'].encode('utf-8')),
                rights=attrs['rights'].encode('utf-8'),
                relation=attrs['relation'].encode('utf-8'),
                format=attrs['format'].encode('utf-8'),
                file_link=attrs['file_link'].encode('utf-8'),
                file_link_local=attrs['file_link_local'].encode('utf-8'),
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

class NySemMultimedia(NyAttributes, semmultimedia_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemMultimedia.gif'
    icon_marked = 'misc_/NaayaContent/NySemMultimedia_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += semmultimedia_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, creator, creator_email, 
        rights, type_multimedia, source, source_link, subject, relation, file_link, 
        file_link_local, format, contributor, releasedate, lang):
        """ """
        self.id = id
        semmultimedia_item.__dict__['__init__'](self, title, description, coverage, keywords, 
            sortorder, creator, creator_email, rights, type_multimedia, source, source_link, 
            subject, relation, file_link, file_link_local, format, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declareProtected(view, 'resource_type')
    def resource_type(self):
        return self.type_multimedia

    security.declareProtected(view, 'resource_subject')
    def resource_subject(self):
        return ' '.join(self.subject)

#    security.declarePrivate('objectkeywords')
#    def objectkeywords(self, lang):
#        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('type_multimedia', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'rights="%s" type_multimedia="%s" file_link="%s" file_link_local="%s" source_link="%s" subject="%s" relation="%s" creator_email="%s" format="%s"' % \
               (self.utXmlEncode(self.rights),
                self.utXmlEncode(self.type_multimedia),
                self.utXmlEncode(self.file_link),
                self.utXmlEncode(self.file_link_local),
                self.utXmlEncode(self.source_link),
                self.utXmlEncode(self.subject),
                self.utXmlEncode(self.relation),
                self.utXmlEncode(self.creator_email),
                self.utXmlEncode(self.format))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
            ra('<creator lang="%s"><![CDATA[%s]]></creator>' % (l, self.utToUtf8(self.getLocalProperty('creator', l))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>%s</dc:type>' % self.utXmlEncode(self.type_multimedia))
        ra('<dc:format>%s</dc:format>' % self.utXmlEncode(self.format))
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(self.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:relation>%s</dc:relation>' % self.utXmlEncode(self.relation))
        ra('<dc:rights>%s</dc:rights>' % self.utXmlEncode(self.rights))
        for k in self.subject:
            if k:
                theme_ob = self.getPortalThesaurus().getThemeByID(k, self.gl_get_selected_language())
                theme_name = theme_ob.theme_name
                if theme_name:
                    ra('<dc:subject>%s</dc:subject>' % self.utXmlEncode(theme_name.strip()))

        ra('<ut:creator_email>%s</ut:creator_email>' % self.utXmlEncode(self.creator_email))
        ra('<ut:type_multimedia>%s</ut:type_multimedia>' % self.utXmlEncode(self.type_multimedia))
        ra('<ut:file_link>%s</ut:file_link>' % self.utXmlEncode(self.file_link))
        ra('<ut:file_link_local>%s</ut:file_link_local>' % self.utXmlEncode(self.file_link_local))
        ra('<ut:source_link>%s</ut:source_link>' % self.utXmlEncode(self.source_link))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='', sortorder='', creator='', 
            creator_email='', rights='', type_multimedia='', source='', source_link='', subject='', 
            relation='', file_link='', file_link_local='', format='', approved='',
            releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        subject = self.utConvertToList(subject)
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, creator, creator_email, 
            rights, type_multimedia, source, source_link, subject, relation, file_link, 
            file_link_local, format, releasedate, lang)
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
        self.type_multimedia = self.version.type_multimedia
        self.file_link = self.version.file_link
        self.file_link_local = self.version.file_link_local
        self.source = self.version.source
        self.source_link = self.version.source_link
        self.subject = self.version.subject
        self.relation = self.version.relation
        self.coverage = self.version.coverage
        self.creator = self.version.creator
        self.creator_email = self.version.creator_email
        self.rights = self.version.rights
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
        self.version = semmultimedia_item(self.title, self.description, self.coverage, self.keywords, self.sortorder, 
            self.creator, self.creator_email, self.rights, self.type_multimedia, self.source, self.source_link, 
            self.subject, self.relation, self.file_link, self.file_link_local, self.format,
            self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='', sortorder='', creator='', 
            creator_email='', rights='', type_multimedia='', source='', source_link='', subject='', 
            relation='', file_link='', file_link_local='', format='', approved='', releasedate='',
            discussion='', lang=None, REQUEST=None, RESPONSE=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        subject = self.utConvertToList(subject)
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            creator=creator, creator_email=creator_email, rights=rights, type_multimedia=type_multimedia, \
            source=source, source_link=source_link, subject=subject, relation=relation, \
            file_link=file_link, file_link_local=file_link_local, format=format)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder, creator, creator_email, 
                        rights, type_multimedia, source, source_link, subject, relation, file_link, 
                        file_link_local, format, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder, creator, creator_email, 
                        rights, type_multimedia, source, source_link, subject, relation, file_link, 
                        file_link_local, format, releasedate, lang)
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
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    creator=creator, creator_email=creator_email, rights=rights, type_multimedia=type_multimedia, \
                    source=source, source_link=source_link, subject=subject, relation=relation, \
                    file_link=file_link, file_link_local=file_link_local, format=format)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semmultimedia_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semmultimedia_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'semedit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semmultimedia_edit')

InitializeClass(NySemMultimedia)