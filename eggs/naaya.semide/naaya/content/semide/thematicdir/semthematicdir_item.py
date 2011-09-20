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
# Kacso Lehel, Finsiel Romania
# Alexandru Plugaru, Eau de Web

#Python
import locale
import operator
import os
import sys

#Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile

#Product imports
from Products.NaayaBase.constants import *
from Products.Naaya.constants import *
from Products.NaayaContent.constants import *
from Products.NaayaCore.constants import *

from Products.Naaya.NyFolder import NyFolder
from Products.NaayaCore.managers.utils import batch_utils
from Products.Naaya.adapters import FolderMetaTypes

#This is wrong
from naaya.content.url                                import url_item ; METATYPE_NYURL = url_item.config['meta_type']
from naaya.content.document                           import document_item; METATYPE_NYDOCUMENT = document_item.config['meta_type']
from naaya.content.exfile                             import exfile_item; METATYPE_NYEXFILE = exfile_item.config['meta_type']

from naaya.content.semide.news.semnews_item           import METATYPE_OBJECT as METATYPE_NYSEMNEWS
from naaya.content.semide.event.semevent_item         import METATYPE_OBJECT as METATYPE_NYSEMEVENT
from naaya.content.semide.project.semproject_item     import METATYPE_OBJECT as METATYPE_NYSEMPROJECT
from naaya.content.semide.document.semdocument_item   import METATYPE_OBJECT as METATYPE_NYSEMDOCUMENT
from naaya.content.semide.multimedia.semmultimedia_item  import METATYPE_OBJECT as METATYPE_NYSEMMULTIMEDIA #Deprecated
from naaya.content.semide.textlaws.semtextlaws_item   import METATYPE_OBJECT as METATYPE_NYSEMTEXTLAWS

from naaya.i18n.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyValidation import NyValidation


#module constants
METATYPE_OBJECT =       'Naaya Semide Thematic Folder'
LABEL_OBJECT =          'Thematic Folder'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Thematic Folder'
OBJECT_FORMS =          ['semthematicdir_add', 'semthematicdir_edit', 'semthematicdir_index']
OBJECT_CONSTRUCTORS =   ['manage_addNySemThematicDir_html', 'semthematicdir_add_html', 'addNySemThematicDir', 'importNySemThematicDir']
OBJECT_ADD_FORM =       'semthematicdir_add_html'
DESCRIPTION_OBJECT =    'This is Naaya Semide Thematic Folder type.'
PREFIX_OBJECT =         'themdir'
PROPERTIES_OBJECT = {
    'id':                   (0, '', ''),
    'title':                (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':          (0, '', ''),
    'coverage':             (0, '', ''),
    'keywords':             (0, '', ''),
    'criteria_keywords':    (0, '', ''),
    'sortorder':            (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':          (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'criteria_date':        (0, MUST_BE_DATETIME, 'The Display objects released after field must contain a valid date.'),
    'discussion':           (0, '', ''),
    'maintainer_email':     (0, '', ''),
    'themes':               (0, '', ''),
    'lang':                 (0, '', '')
}

DEFAULT_SCHEMA = {}

config = {
    'product': 'NaayaContent',
    'module': 'NySemThematicDir',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_OBJECT,
    'label': LABEL_OBJECT,
    'permission': PERMISSION_ADD_OBJECT,
    'forms': OBJECT_FORMS,
    'add_form': OBJECT_ADD_FORM,
    'description': DESCRIPTION_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'schema_name': 'NySemThematicDir',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'NySemThematicDir.gif'),
    '_misc': {
            'NySemThematicDir.gif': ImageFile('www/NySemThematicDir.gif', globals()),
            'NySemThematicDir_marked.gif': ImageFile('www/NySemThematicDir_marked.gif', globals()),
        },
}

manage_addNySemThematicDir_html = PageTemplateFile('zpt/semthematicdir_manage_add', globals())
manage_addNySemThematicDir_html.kind = METATYPE_OBJECT
manage_addNySemThematicDir_html.action = 'addNySemThematicDir'

def semthematicdir_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemThematicDir'}, 'semthematicdir_add')

def addNySemThematicDir(self, id='', title='', description='', coverage='', keywords='',
    criteria_keywords='', sortorder='', publicinterface='', maintainer_email='',
    folder_meta_types=None, contributor=None, releasedate='', criteria_date='', discussion='',
    themes='', lang=None, REQUEST=None, **kwargs):
    """
    Create an object of Thematic Folder type.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)
    if publicinterface: publicinterface = 1
    else: publicinterface = 0
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if folder_meta_types==None:
        folder_meta_types = [METATYPE_FOLDER, METATYPE_NYURL, METATYPE_NYEXFILE, METATYPE_NYDOCUMENT]
    elif folder_meta_types == '':
        folder_meta_types = []
    else: folder_meta_types = self.utConvertToList(folder_meta_types)
    themes = self.utConvertToList(themes)

    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'semthematicdir_manage_add' or l_referer.find('semthematicdir_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, criteria_keywords=criteria_keywords, sortorder=sortorder, \
            releasedate=releasedate, criteria_date=criteria_date, maintainer_email=maintainer_email, \
            discussion=discussion, themes=themes
            )
    else:
        r = []
    if not len(r):
        #process parameters
        if lang is None: lang = self.gl_get_selected_language()
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        criteria_date = self.process_releasedate(criteria_date)
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NySemThematicDir(id, title, description, coverage,
                    keywords, criteria_keywords, sortorder, publicinterface, maintainer_email, contributor,
                    folder_meta_types, releasedate, criteria_date, themes, lang)
        self.gl_add_languages(ob)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        if publicinterface:
            ob.publicinterface = publicinterface
            ob.convert_publicinterface_to_custom_index()
            ob.manage_create_custom_template()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(ob.getSite(), ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'semthematicdir_manage_add' or l_referer.find('semthematicdir_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'semthematicdir_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                criteria_keywords=criteria_keywords, sortorder=sortorder, \
                releasedate=releasedate, criteria_date=criteria_date, \
                maintainer_email=maintainer_email, discussion=discussion, themes=themes, lang=lang)
            REQUEST.RESPONSE.redirect('%s/semthematicdir_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNySemThematicDir(self, param, id, attrs, content, properties, discussion, objects):
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
            publicinterface = abs(int(attrs['publicinterface'].encode('utf-8')))
            meta_types = attrs['folder_meta_types'].encode('utf-8')
            if meta_types == '': meta_types = ''
            else: meta_types = meta_types.split(',')
            #create the object
            addNySemThematicDir(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                publicinterface=publicinterface,
                maintainer_email=attrs['maintainer_email'].encode('utf-8'),
                folder_meta_types=meta_types,
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))),
                themes=self.parseValue(attrs['themes'].encode('utf-8')))
            ob = self._getOb(id)
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            if attrs['criteria_date'].encode('utf-8') != '':
                ob.setCriteriaDate(attrs['criteria_date'].encode('utf-8'))
            if publicinterface:
                l_index = ob._getOb('index', None)
                if l_index is not None:
                    l_index.pt_edit(text=content, content_type='')
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)
        #go on and import sub objects
        for object in objects:
            ob.import_data(object)

class NySemThematicDir(NyFolder):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon        = 'misc_/NaayaContent/NySemThematicDir.gif'
    icon_marked = 'misc_/NaayaContent/NySemThematicDir_marked.gif'

    security = ClassSecurityInfo()

    criteria_keywords = LocalProperty('criteria_keywords')

    def all_meta_types(self, interfaces=None):
        """ What can you put inside me? """
        #filter meta types
        l = list(filter(lambda x: x['name'] in [METATYPE_FOLDER, METATYPE_NYURL, METATYPE_NYEXFILE, METATYPE_NYDOCUMENT], Products.meta_types))
        #handle uninstalled pluggable meta_types
        pluggable_meta_types = self.get_pluggable_metatypes()
        pluggable_installed_meta_types = self.get_pluggable_installed_meta_types()
        t = copy(l)
        for x in t:
            if (x['name'] in pluggable_meta_types) and (x['name'] not in pluggable_installed_meta_types):
                l.remove(x)
        return l

    def __init__(self, id='', title='', description='', coverage='',
                    keywords='', criteria_keywords='', sortorder='', publicinterface='', maintainer_email='', contributor='',
                    folder_meta_types='', releasedate='', criteria_date='', themes='', lang=''):
        NyFolder.__dict__['__init__'](self, id, title, description, coverage,
            keywords, sortorder, publicinterface, maintainer_email, contributor,
            folder_meta_types, releasedate, lang)
        self.themes = themes
        self.criteria_date = criteria_date
        self._setLocalPropValue('criteria_keywords', lang, criteria_keywords)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        meta_types = FolderMetaTypes(self).get_values()
        return 'custom_index="%s" maintainer_email="%s" folder_meta_types="%s" themes="%s" criteria_date="%s"' % \
            (self.utXmlEncode(self.compute_custom_index_value()),
                self.utXmlEncode(self.maintainer_email),
                self.utXmlEncode(','.join(meta_types)),
                self.utXmlEncode(self.themes),
                self.utXmlEncode(self.criteria_date))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<criteria_keywords lang="%s"><![CDATA[%s]]></criteria_keywords>' % (l, self.utToUtf8(self.getLocalProperty('criteria_keywords', l))))
        return ''.join(r)


    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semthematicdir_edit')

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semthematicdir_index')

    def hasVersion(self):
        """
        Checks if the object is locked.
        @return:
            - B{TRUE/1} if true
            - B{FALSE/0} otherwise
        """
        return 0

    def format_results(self, p_objects=[], skey='', rkey='', ps_start=''):
        """Return sorted events"""
        results = []
        res_per_page = 10
        try:    ps_start = int(ps_start)
        except: ps_start = 0
        try:    rkey = int(rkey)
        except: rkey = 0

        if skey == 'date':
            p_objects.sort(lambda x,y: cmp(y.bobobase_modification_time(), x.bobobase_modification_time()))
            results.extend(p_objects)
        else:
            l_objects = self.utSortObjsByLocaleAttr(p_objects, skey, rkey, self.gl_get_selected_language())
            results.extend(l_objects)

        #batch related
        batch_obj = batch_utils(res_per_page, len(results), ps_start)
        if len(results) > 0:
            paging_informations = batch_obj.butGetPagingInformations()
        else:
            paging_informations = (-1, 0, 0, -1, -1, 0, res_per_page, [0])
        return (paging_informations, (1, 1, results[paging_informations[0]:paging_informations[1]]))

    security.declareProtected(view, 'getThDirPortletsData')
    def getThDirPortletsData(self, skey='', rkey='', ps_start=''):
        """
        Returns a list of news, events, projects and all the rest of the object types
        """
        #return nothing if no themes were selected
        if self.themes==[''] and self.criteria_keywords=='': return [[],[],[],[]]
        #query the thesaurus for concepts
        lang = self.gl_get_selected_language()
        th_list = self.themes
        added_any_word = False
        portal_thesaurus = self.getPortalThesaurus()
        l_allconcepts = {}
        l_additional_concepts = {}
        for lang in self.gl_get_languages():
            l_allconcepts[lang] = []
            l_additional_concepts[lang] = []
            if th_list != ['']:
                for theme_id in th_list:
                    terms_list = []
                    for k in portal_thesaurus.getThemeConcept(theme_id, lang):
                        if k.concept_name: terms_list.append(k.concept_name)
                    if terms_list != ['']:
                        added_any_word = True
                        l_allconcepts[lang].extend(terms_list)
            l_additional = self.getLocalProperty('criteria_keywords', lang)
            l_additional_list = [x.strip() for x in l_additional.split(',') if x.strip()!='']
            l_additional_concepts[lang].extend(l_additional_list)
            if l_additional_list != ['']:
                l_allconcepts[lang].extend(l_additional_list)
                added_any_word = True

        if added_any_word:
            ThesaurusData = self.getThDirPortletsDataSpecific
            l_news     = ThesaurusData(l_allconcepts, l_additional_concepts, p_news=1, p_amount=5)
            l_events   = ThesaurusData(l_allconcepts, l_additional_concepts, p_events=1, p_amount=5)
            l_projects = ThesaurusData(l_allconcepts, l_additional_concepts, p_projects=1, p_amount=0)

            l_rest     = ThesaurusData(l_allconcepts, l_additional_concepts, p_amount=0)
            l_rest     = self.format_results(l_rest, skey, rkey, ps_start)

            return [l_news, l_events, l_projects, l_rest]
        else:
            return [[],[],[],[]]


    security.declareProtected(view, 'getThDirPortletsData')
    def getThDirPortletsDataSpecific(self, p_allconcepts, p_additional_list, p_news=0, p_events=0, p_projects=0, p_amount=0,):
        """
        Returns a list of specific object type
        """
        results = []
        l_meta = []
        l_meta_sbj = []
        lang = self.gl_get_selected_language()
        obs_with_subject = [METATYPE_NYSEMDOCUMENT, METATYPE_NYSEMMULTIMEDIA, METATYPE_NYSEMTEXTLAWS, \
                            METATYPE_NYSEMNEWS, METATYPE_NYSEMEVENT, METATYPE_NYSEMPROJECT]

        #decide the searchable metatypes
        if p_news:
            l_meta.append(METATYPE_NYSEMNEWS)
        elif p_events:
            l_meta.append(METATYPE_NYSEMEVENT)
        elif p_projects:
            l_meta.append(METATYPE_NYSEMPROJECT)
        else:
            l_meta.extend(self.get_pluggable_installed_meta_types())
            l_meta.append(METATYPE_FOLDER)
            l_meta.remove(METATYPE_NYSEMNEWS)
            l_meta.remove(METATYPE_NYSEMEVENT)
            l_meta.remove(METATYPE_NYSEMPROJECT)
            l_meta.remove(self.meta_type)

        for k in l_meta:
            if k in obs_with_subject:
                l_meta_sbj.append(k)
                l_meta.remove(k)

        res = []
        #search for objects with subject property
        query = {}
        if l_meta_sbj:
            if self.themes != ['']:
                for th in self.themes:
                    expr = 'self.getCatalogedObjects(meta_type=l_meta_sbj, approved=1, resource_subject=th, releasedate=self.criteria_date, releasedate_range=\'min\')'
                    res.extend(eval(expr))

        #search for objects without subject property
        query = {}
        if l_meta:
            for lang in self.gl_get_languages():
                if len(p_allconcepts[lang]):
                    #split the lists of concepts
                    l_nos = range(0, len(p_allconcepts[lang]), 100)
                    l_nos2 = l_nos[:]
                    l_nos2.remove(0)
                    l_nos2.append(len(p_allconcepts[lang])+1)
                    l_nos2 = [x-1 for x in l_nos2]
                    l_concepts = {}
                    l_concepts[lang] = [p_allconcepts[lang][l_nos[i]:l_nos2[i]] for i in range(len(l_nos))]

                    for sub_list in l_concepts[lang]:
                        query[lang] = ' or '.join(['"%s"' % self.utStrEscapeForSearch(x) for x in sub_list])
                        expr = 'self.getCatalogedObjects(meta_type=l_meta, approved=1, objectkeywords_%s=query[\'%s\'], releasedate=self.criteria_date, releasedate_range=\'min\')' % (lang, lang)
                        res.extend(eval(expr))

        #search after additional keywords
        query = {}
        all_meta = []
        all_meta.extend(l_meta_sbj)
        all_meta.extend(l_meta)
        for l_meta in all_meta:
            for lang in self.gl_get_languages():
                if p_additional_list[lang]:
                    query[lang] = ' or '.join(['"%s"' % self.utStrEscapeForSearch(x) for x in p_additional_list[lang]])
                    expr = 'self.getCatalogedObjects(meta_type=l_meta, approved=1, objectkeywords_%s=query[\'%s\'], releasedate=self.criteria_date, releasedate_range=\'min\')' % (lang, lang)
                    res.extend(eval(expr))

        results = self.utEliminateDuplicatesByURL(res)

        if p_amount:
            results.sort(lambda x,y: cmp(y.bobobase_modification_time(), x.bobobase_modification_time()))
            return results[:p_amount]
        return results


    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semthematicdir_manage_edit', globals())

#    security.declareProtected(view_management_screens, 'manage_folder_subobjects_html')
#    manage_folder_subobjects_html = PageTemplateFile('zpt/semthematicdir_manage_subobjects', globals())

    security.declarePrivate('setReleaseDate')
    def setCriteriaDate(self, criteria_date):
        """
        Set the release date of the current object.
        @param releasedate: the date
        @type releasedate: DateTime
        """
        self.criteria_date = self.utGetDate(criteria_date)
        self._p_changed = 1

    #utils
    def utSortObjsByLocaleAttr(self, p_list, p_attr, p_desc=1, p_locale=''):
        """Sort a list of objects by an attribute values based on locale"""
        if not p_locale:
            #normal sorting
            l_len = len(p_list)
            l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
            l_temp.sort()
            if p_desc: l_temp.reverse()
            return map(operator.getitem, l_temp, (-1,)*l_len)
        else:
            #locale sorting based
            try:
                default_locale = locale.setlocale(locale.LC_ALL)

                try:
                    #try to set for NT, WIN operating systems
                    locale.setlocale(locale.LC_ALL, p_locale)
                except:
                    #try to set for other operating system
                    if p_locale == 'ar': p_locale = 'ar_DZ'
                    else:                p_locale = '%s_%s' % (p_locale, p_locale.upper())
                    locale.setlocale(locale.LC_ALL, p_locale)

                #sorting
                l_len = len(p_list)
                l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
                l_temp.sort(lambda x, y: locale.strcoll(x[0], y[0]))
                if p_desc: l_temp.reverse()

                locale.setlocale(locale.LC_ALL, default_locale)
                return map(operator.getitem, l_temp, (-1,)*l_len)
            except:
                #in case of failure make a normal sorting
                locale.setlocale(locale.LC_ALL, default_locale)
                return self.utSortObjsByLocaleAttr(p_list, p_attr, p_desc)

InitializeClass(NyFolder)

config.update({
    'constructors': (manage_addNySemThematicDir_html, addNySemThematicDir),
    'folder_constructors': [
            ('manage_addNySemThematicDir_html', manage_addNySemThematicDir_html),
            ('semthematicdir_add_html', semthematicdir_add_html),
            ('addNySemThematicDir', addNySemThematicDir),
        ],
    'add_method': addNySemThematicDir,
    'validation': issubclass(NySemThematicDir, NyValidation),
    '_class': NySemThematicDir,
})

def get_config():
    return config
