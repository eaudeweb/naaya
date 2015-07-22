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
# Alexandru Ghica, Finsiel Romania

#Python imports
from os.path import join

#Zope imports
from Globals                                    import InitializeClass
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate    import manage_addPageTemplate
import Products

#Product imports
from Products.NaayaBase.constants       import *
from Products.Naaya.constants           import *
from Products.NaayaContent.constants    import *
from Products.NaayaCore.constants       import *
from Products.NaayaBase.managers.import_parser          import import_parser
from Products.Naaya.NyFolder                            import NyFolder, addNyFolder
from Products.NaayaContent.NyURL.NyURL                  import addNyURL
from Products.NaayaContent.NyFile.NyFile                import addNyFile
from Products.NaayaContent.NySemNews.NySemNews          import METATYPE_OBJECT as METATYPE_NYSEMNEWS
from Products.NaayaContent.NySemEvent.NySemEvent        import METATYPE_OBJECT as METATYPE_NYSEMEVENT
from Products.NaayaContent.NySemProject.NySemProject    import METATYPE_OBJECT as METATYPE_NYSEMPROJECT
from Products.Localizer.LocalPropertyManager            import LocalProperty
from Products.NaayaCore.PortletsTool.HTMLPortlet        import addHTMLPortlet
from Products.NaayaCore.SyndicationTool.RemoteChannel   import manage_addRemoteChannel

#module constants
METATYPE_OBJECT =       'Naaya Country Folder'
LABEL_OBJECT =          'Country Folder'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Country objects'
OBJECT_FORMS =          ['country_add', 'country_edit', 'country_index', 'country_editportlet', 'country_custom_header', 'country_custom_footer']
OBJECT_CONSTRUCTORS =   ['manage_addNyCountry_html', 'country_add_html', 'addNyCountry', 'importNyCountry']
OBJECT_ADD_FORM =       'country_add_html'
DESCRIPTION_OBJECT =    'This is Naaya Country type.'
PREFIX_OBJECT =         'country'
PROPERTIES_OBJECT = {
    'id':                   (0, '', ''),
    'title':                (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':          (0, '', ''),
    'coverage':             (0, '', ''),
    'keywords':             (0, '', ''),
    'sortorder':            (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':          (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':           (0, '', ''),
    'nfp_label':            (0, '', ''),
    'nfp_url':              (0, '', ''),
    'source':               (0, '', ''),
    'flag_file':            (0, '', ''),
    'flag_url':             (0, '', ''),
    'del_smallflag':        (0, '', ''),
    'link_ins':             (0, '', ''),
    'link_doc':             (0, '', ''),
    'link_train':           (0, '', ''),
    'link_rd':              (0, '', ''),
    'link_data':            (0, '', ''),
    'legislation_feed_url': (0, '', ''),
    'project_feed_url':     (0, '', ''),
    'lang':                 (0, '', '')
}

manage_addNyCountry_html = PageTemplateFile('zpt/country_manage_add', globals())
manage_addNyCountry_html.kind = METATYPE_OBJECT
manage_addNyCountry_html.action = 'addNyCountry'

def country_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyCountry'}, 'country_add')

def addNyCountry(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', nfp_label='', nfp_url='', source='file', flag_file='', flag_url='',
    link_ins='', link_doc='', link_train='', link_rd='', link_data='', legislation_feed_url='',
    project_feed_url='', publicinterface='', folder_meta_types='', contributor=None,
    releasedate='', discussion='', lang=None, load_default_data=1, REQUEST=None, **kwargs):
    """
    Create an object of Country type.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    if publicinterface: publicinterface = 1
    else: publicinterface = 0
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if folder_meta_types == '': folder_meta_types = []
    else: folder_meta_types = self.utConvertToList(folder_meta_types)
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'country_manage_add' or l_referer.find('country_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            nfp_label=nfp_label, nfp_url=nfp_url, source=source, flag_file=flag_file, flag_url=flag_url, \
            link_ins=link_ins, link_doc=link_doc, link_train=link_train, link_rd=link_rd, link_data=link_data, \
            legislation_feed_url=legislation_feed_url, project_feed_url=project_feed_url)
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

        #create object
        ob = NyCountry(id, title, description, coverage, keywords, sortorder,
                None, nfp_label, nfp_url, link_ins, link_doc, link_train, link_rd,
                link_data, publicinterface, contributor, folder_meta_types, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.setSmallFlag(source, flag_file, flag_url)
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        ob.createPublicInterface()
        if discussion: ob.open_for_comments()
        if load_default_data: ob.loadDefaultData(lang, legislation_feed_url, project_feed_url)
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(ob.getSite(), ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'country_manage_add' or l_referer.find('country_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'country_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, \
                sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                nfp_label=nfp_label, nfp_url=nfp_url, source=source, flag_url=flag_url, \
                link_ins=link_ins, link_doc=link_doc, link_train=link_train, link_rd=link_rd, link_data=link_data, \
                legislation_feed_url=legislation_feed_url, project_feed_url=project_feed_url, lang=lang)
            REQUEST.RESPONSE.redirect('%s/country_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNyCountry(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    ob = self._getOb(id, None)
    if param in [0, 1] or (param==2 and ob is None):
        if param == 1:
            #delete the object if exists
            try: self.manage_delObjects([id])
            except: pass
        addNyCountry(self, id=id,
            sortorder=attrs['sortorder'].encode('utf-8'),
            flag_file=self.utBase64Decode(attrs['smallflag'].encode('utf-8')),
            legislation_feed_url=attrs['legislation_feed_url'].encode('utf-8'),
            project_feed_url=attrs['project_feed_url'].encode('utf-8'),
            contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
            discussion=abs(int(attrs['discussion'].encode('utf-8'))),
            load_default_data=0)
        ob = self._getOb(id)
        for property, langs in properties.items():
            for lang in langs:
                ob._setLocalPropValue(property, lang, langs[lang])
        ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
            approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
        if attrs['releasedate'].encode('utf-8') != '':
            ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
        ob.import_comments(discussion)
        self.recatalogNyObject(ob)
    #go on and import portlets and remote channels
    for object in objects:
        if object.meta_type == "Naaya HTML Portlet":
            addHTMLPortlet(ob, id=object.id.encode('utf-8'))
            ob_portlet = ob._getOb(object.id)
            for property, langs in object.properties.items():
                for lang in langs:
                    if len(langs[lang]) > 0:
                        ob_portlet._setLocalPropValue(property, lang, langs[lang])
        elif object.meta_type == "Naaya Remote Channel":
            manage_addRemoteChannel(ob, id=object.attrs['id'].encode('utf-8'),
                                        title=object.attrs['title'].encode('utf-8'),
                                        url=object.attrs['url'].encode('utf-8'),
                                        numbershownitems=object.attrs['numbershownitems'].encode('utf-8'))
        else:
            ob.import_data(object)

class NyCountry(NyFolder):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyCountry.gif'
    icon_marked = 'misc_/NaayaContent/NyCountry_marked.gif'

    manage_options = (
        NyFolder.manage_options
    )

    security = ClassSecurityInfo()

    nfp_label =     LocalProperty('nfp_label')
    nfp_url =       LocalProperty('nfp_url')
    link_ins =      LocalProperty('link_ins')
    link_doc =      LocalProperty('link_doc')
    link_train =    LocalProperty('link_train')
    link_rd =       LocalProperty('link_rd')
    link_data =     LocalProperty('link_data')

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        smallflag, nfp_label, nfp_url, link_ins, link_doc, link_train, link_rd, link_data,
        publicinterface, contributor, folder_meta_types, releasedate, lang):
        """ """
        NyFolder.__dict__['__init__'](self, id, title, description, coverage,
            keywords, sortorder, publicinterface, '', contributor,
            folder_meta_types, releasedate, lang)
        self._setLocalPropValue('nfp_label',    lang, nfp_label)
        self._setLocalPropValue('nfp_url',      lang, nfp_url)
        self._setLocalPropValue('link_ins',     lang, link_ins)
        self._setLocalPropValue('link_doc',     lang, link_doc)
        self._setLocalPropValue('link_train',   lang, link_train)
        self._setLocalPropValue('link_rd',      lang, link_rd)
        self._setLocalPropValue('link_data',    lang, link_data)
        self.smallflag = smallflag

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, lang, legislation_feed_url, project_feed_url):
        """ """
        #load country folder skeleton - default content
        path = join(NAAYACONTENT_PRODUCT_PATH, 'NyCountry', 'skel.nyexp')
        import_handler, error = import_parser().parse(self.futRead(path, 'r'))
        if import_handler is not None:
            for object in import_handler.root.objects:
                self.import_data(object)
        else:
            raise Exception, EXCEPTION_PARSINGFILE % (path, error)
        #create right portlets
        addHTMLPortlet(self, id=self.get_portlet_indicators_id(),
            title='Key indicators', lang=lang)
        addHTMLPortlet(self, id=self.get_portlet_reports_id(),
            title='Important reports', lang=lang)
        #create remote channels
        manage_addRemoteChannel(self, id=self.get_rc_legislation_id(),
            title='Legislation on water RSS feed',
            url=legislation_feed_url)
        manage_addRemoteChannel(self, id=self.get_rc_project_id(),
            title='Project water RSS feed',
            url=project_feed_url)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'publicinterface="%s" maintainer_email="%s" folder_meta_types="%s" smallflag="%s" legislation_feed_url="%s" project_feed_url="%s"' % \
            (self.utXmlEncode(self.publicinterface),
                self.utXmlEncode(self.maintainer_email),
                self.utXmlEncode(','.join(self.folder_meta_types)),
                self.utBase64Encode(self.utNoneToEmpty(self.smallflag)),
                self.utXmlEncode(self.get_rc_legislation_url()),
                self.utXmlEncode(self.get_rc_project_url()))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<nfp_label lang="%s"><![CDATA[%s]]></nfp_label>' % (l, self.utToUtf8(self.getLocalProperty('nfp_label', l))))
            ra('<nfp_url lang="%s"><![CDATA[%s]]></nfp_url>' % (l, self.utToUtf8(self.getLocalProperty('nfp_url', l))))
            ra('<link_ins lang="%s"><![CDATA[%s]]></link_ins>' % (l, self.utToUtf8(self.getLocalProperty('link_ins', l))))
            ra('<link_doc lang="%s"><![CDATA[%s]]></link_doc>' % (l, self.utToUtf8(self.getLocalProperty('link_doc', l))))
            ra('<link_train lang="%s"><![CDATA[%s]]></link_train>' % (l, self.utToUtf8(self.getLocalProperty('link_train', l))))
            ra('<link_rd lang="%s"><![CDATA[%s]]></link_rd>' % (l, self.utToUtf8(self.getLocalProperty('link_rd', l))))
            ra('<tooltip lang="%s"><![CDATA[%s]]></tooltip>' % (l, self.utToUtf8(self.getLocalProperty('tooltip', l))))
            ra('<link_data lang="%s"><![CDATA[%s]]></link_data>' % (l, self.utToUtf8(self.getLocalProperty('link_data', l))))
        #portlets and remote channels
        for l_portlet in self.objectValues('Naaya HTML Portlet'):
            ra('<ob meta_type="%s" id="%s" param="0">' % (l_portlet.meta_type, l_portlet.id))
            for l in self.gl_get_languages():
                ra('<title lang="%s"><![CDATA[%s]]></title>' % (l, self.utToUtf8(l_portlet.getLocalProperty('title', l))))
                ra('<body lang="%s"><![CDATA[%s]]></body>' % (l, self.utToUtf8(l_portlet.getLocalProperty('body', l))))
            ra('</ob>')
        for l_channel in self.objectValues('Naaya Remote Channel'):
            ra('<ob meta_type="%s" id="%s" title="%s" url="%s" numbershownitems="%s" param="0"/>' % (l_channel.meta_type, l_channel.id, l_channel.title, l_channel.url, l_channel.numbershownitems))
        return ''.join(r)

    def get_left_portlets_objects(self):
        #get the left portlets objects
        l = ['portlet_country_left']
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, l, (None,)*len(l)))

    def get_right_portlets_objects(self):
        #get the right portlets objects
        l, t = [], self.getPortletsTool()
        p = self.get_portlet_indicators()
        if p is not None: l.append(p)
        p = self.get_portlet_reports()
        if p is not None: l.append(p)
        p = t._getOb('portlet_country_news')
        if p is not None: l.append(p)
        p = t._getOb('portlet_country_events')
        if p is not None: l.append(p)
        p = t._getOb('portlet_country_projects')
        if p is not None: l.append(p)
        return l

    def hasVersion(self):
        """
        Checks if the object is locked.
        @return:
            - B{TRUE/1} if true
            - B{FALSE/0} otherwise
        """
        return 0

    def hasLinksValues(self):
        """
        Checks if the object has at least one link value.
        @return:
            - B{TRUE/1} if true
            - B{FALSE/0} otherwise
        """
        return self.utLinkValue(self.link_ins) or self.utLinkValue(self.link_doc) or \
            self.utLinkValue(self.link_train) or self.utLinkValue(self.link_rd) or \
            self.utLinkValue(self.link_data)

    #api
    def get_country_object(self):           return self
    def get_country_object_title(self, lang='en'):     return self.utToUtf8(self.getLocalProperty('title', lang))
    def get_country_object_path(self, p=0): return self.absolute_url(p)
 
    def get_portlet_indicators_id(self):    return '%sindicators' % PREFIX_PORTLET
    def get_portlet_indicators(self):       return self._getOb('%sindicators' % PREFIX_PORTLET, None)
    def get_portlet_reports_id(self):       return '%sreports' % PREFIX_PORTLET
    def get_portlet_reports(self):          return self._getOb('%sreports' % PREFIX_PORTLET, None)

    def get_rc_legislation_id(self):        return 'rclegislation'
    def get_rc_legislation(self):           return self._getOb('rclegislation', None)
    def get_rc_legislation_url(self):       return self._getOb('rclegislation', None).url
    def get_rc_project_id(self):            return 'rcproject'
    def get_rc_project(self):               return self._getOb('rcproject', None)
    def get_rc_project_url(self):           return self._getOb('rcproject', None).url

    def getCountryNews(self):
        #returns a list with news related with the country
        l_search_key = self.getLocalProperty('title', 'en') + ' or ' + self.getLocalProperty('coverage', 'en')
        expr = 'self.getCatalogedObjects(meta_type=\'%s\', approved=1, howmany=5, coverage_%s=l_search_key)' % (METATYPE_NYSEMNEWS, 'en')
        return eval(expr)

    def getCountryEvents(self):
        #returns a list with upcoming events related with the country
        l_search_key = self.getLocalProperty('title', 'en') + ' or ' + self.getLocalProperty('coverage', 'en')
        expr = 'self.getCatalogedObjects(meta_type=\'%s\', approved=1, howmany=5, coverage_%s=l_search_key)' % (METATYPE_NYSEMEVENT, 'en')
        return eval(expr)

    def getCountryProjects(self):
        #returns a list with projects related with the country
        l_search_key = self.getLocalProperty('coverage', 'en')
        expr = 'self.getCatalogedObjects(meta_type=\'%s\', approved=1, coverage_%s=l_search_key)' % (METATYPE_NYSEMPROJECT, 'en')
        return eval(expr)

    def getCountryContent(self):
        #returns the contained objects sorted by sort order
        return self.utSortObjsListByAttr([x for x in self.objectValues(self.searchable_content) if x.approved == 1], 'sortorder', 0)

    def inCountryTopic(self, p_topic, p_location):
        #test if the given location is in the context of a country topic
        if isinstance(p_topic, str):
            page = self.REQUEST['URL'].split('/')[-1]
            return page == p_topic
        if p_location == self: return 0
        else:
            l_parent = p_location
            while l_parent.getParentNode() != self:
                l_parent = l_parent.getParentNode()
            return p_topic == l_parent

    def getSmallFlag(self, REQUEST=None):
        """ """
        return self.smallflag

    def hasSmallFlag(self):
        return self.smallflag is not None

    def setSmallFlag(self, source, file, url):
        """
        Upload the small flag.
        """
        if source == 'file':
            if file != '':
                if hasattr(file, 'filename'):
                    if file.filename != '':
                        l_read = file.read()
                        if l_read != '':
                            self.smallflag = l_read
                            self._p_changed = 1
                else:
                    self.smallflag = file
                    self._p_changed = 1
        elif source == 'url':
            if url != '':
                l_data, l_ctype = self.grabFromUrl(url)
                if l_data is not None:
                    self.smallflag = l_data
                    self._p_changed = 1

    def delSmallFlag(self):
        """
        Delete the small flag.
        """
        self.smallflag = None
        self._p_changed = 1

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', publicinterface='', approved='', source='file', flag_file='',
        flag_url='', del_smallflag='', nfp_label='', nfp_url='', link_ins='', link_doc='',
        link_train='', link_rd='', link_data='', legislation_feed_url='', project_feed_url='',
        releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if publicinterface: publicinterface = 1
        else: publicinterface = 0
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title',        lang, title)
        self._setLocalPropValue('description',  lang, description)
        self._setLocalPropValue('coverage',     lang, coverage)
        self._setLocalPropValue('keywords',     lang, keywords)
        self._setLocalPropValue('nfp_label',    lang, nfp_label)
        self._setLocalPropValue('nfp_url',      lang, nfp_url)
        self._setLocalPropValue('link_ins',     lang, link_ins)
        self._setLocalPropValue('link_doc',     lang, link_doc)
        self._setLocalPropValue('link_train',   lang, link_train)
        self._setLocalPropValue('link_rd',      lang, link_rd)
        self._setLocalPropValue('link_data',    lang, link_data)
        self.sortorder =        sortorder
        self.publicinterface =  publicinterface
        self.approved =         approved
        self.releasedate =      releasedate
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
        if del_smallflag != '': self.delSmallFlag()
        else: self.setSmallFlag(source, flag_file, flag_url)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        self.createPublicInterface()
        #update remote channels feeds
        self.get_rc_legislation().set_new_feed_url(legislation_feed_url)
        self.get_rc_project().set_new_feed_url(project_feed_url)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', source='file', flag_file='', flag_url='', del_smallflag='',
        nfp_label='', nfp_url='', link_ins='', link_doc='', link_train='', link_rd='',
        link_data='', legislation_feed_url='', project_feed_url='', releasedate='',
        discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            nfp_label=nfp_label, nfp_url=nfp_url, source=source, flag_file=flag_file, flag_url=flag_url, \
            link_ins=link_ins, link_doc=link_doc, link_train=link_train, link_rd=link_rd, link_data=link_data, \
            legislation_feed_url=legislation_feed_url, project_feed_url=project_feed_url)
        if not len(r):
            releasedate =       self.process_releasedate(releasedate, self.releasedate)
            sortorder =         int(sortorder)
            self.sortorder =    sortorder
            self.releasedate =  releasedate
            self._setLocalPropValue('title',        lang, title)
            self._setLocalPropValue('description',  lang, description)
            self._setLocalPropValue('coverage',     lang, coverage)
            self._setLocalPropValue('keywords',     lang, keywords)
            self._setLocalPropValue('nfp_label',    lang, nfp_label)
            self._setLocalPropValue('nfp_url',      lang, nfp_url)
            self._setLocalPropValue('link_ins',     lang, link_ins)
            self._setLocalPropValue('link_doc',     lang, link_doc)
            self._setLocalPropValue('link_train',   lang, link_train)
            self._setLocalPropValue('link_rd',      lang, link_rd)
            self._setLocalPropValue('link_data',    lang, link_data)
            if del_smallflag != '': self.delSmallFlag()
            else: self.setSmallFlag(source, flag_file, flag_url)
            self.updatePropertiesFromGlossary(lang)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            self._p_changed = 1
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self.recatalogNyObject(self)
            #update remote channels feeds
            self.get_rc_legislation().set_new_feed_url(legislation_feed_url)
            self.get_rc_project().set_new_feed_url(project_feed_url)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('edit_html?lang=%s' % lang)
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, \
                    sortorder=sortorder, releasedate=releasedate, discussion=discussion, \
                    nfp_label=nfp_label, nfp_url=nfp_url, source=source, flag_url=flag_url, \
                    link_ins=link_ins, link_doc=link_doc, link_train=link_train, link_rd=link_rd, link_data=link_data, \
                    legislation_feed_url=legislation_feed_url, project_feed_url=project_feed_url, \
                    del_smallflag=del_smallflag)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'update_legislation_feed')
    def update_legislation_feed(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        channel = self.get_rc_legislation()
        channel.harvest_feed()
        if REQUEST:
            if channel.get_feed_bozo_exception() is not None: self.setSessionErrors([channel.get_feed_bozo_exception()])
            else: self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/legislation_water/' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'update_project_feed')
    def update_project_feed(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        channel = self.get_rc_project()
        channel.harvest_feed()
        if REQUEST:
            if channel.get_feed_bozo_exception() is not None: self.setSessionErrors([channel.get_feed_bozo_exception()])
            else: self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/project_water/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'editPortlet')
    def editPortlet(self, id='', title='', body='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        ob = self.getObjectById(id)
        if ob is not None:
            ob.manage_properties(title, body, lang)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/editportlet_html?id=%s' % (self.absolute_url(), id))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/country_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'standard_html_header')
    def standard_html_header(self, REQUEST=None, RESPONSE=None, **args):
        """ """
        if not args.has_key('show_edit'): args['show_edit'] = 0
        args['here'] = self.REQUEST.PARENTS[0]
        args['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
        return self.getFormsTool().getContent(args, 'country_custom_header').split('<!--SITE_HEADERFOOTER_MARKER-->')[0]

    security.declareProtected(view, 'standard_html_header')
    def standard_html_footer(self, REQUEST=None, RESPONSE=None):
        """ """
        context = {'here': self.REQUEST.PARENTS[0]}
        context['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
        return self.getFormsTool().getContent(context, 'country_custom_footer').split('<!--SITE_HEADERFOOTER_MARKER-->')[1]

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None: return l_index()
        return self.getFormsTool().getContent({'here': self}, 'country_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'country_edit')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'editportlet_html')
    def editportlet_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'country_editportlet')

InitializeClass(NyCountry)
