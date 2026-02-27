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
# Alexandru Plugaru, Eau de Web

# Python
import os
import sys
from copy import deepcopy

# Zope
import Globals
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from App.ImageFile import ImageFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import zope.event

# Naaya
from naaya.content.base.constants import MUST_BE_NONEMPTY, MUST_BE_POSITIV_INT, MUST_BE_DATETIME
from Products.NaayaBase.constants import (PERMISSION_EDIT_OBJECTS, EXCEPTION_NOTAUTHORIZED,
EXCEPTION_NOTAUTHORIZED_MSG, MESSAGE_SAVEDCHANGES, )
from Products.NaayaCore.constants import PREFIX_PORTLET

from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyValidation import NyValidation

from Products.NaayaCore.managers.utils import make_id
from Products.NaayaBase.managers.import_parser import import_parser
from Products.Naaya.NyFolder import NyFolder
from Products.Naaya.adapters import FolderMetaTypes

from naaya.content.semide.news.semnews_item import METATYPE_OBJECT as METATYPE_NYSEMNEWS
from naaya.content.semide.event.semevent_item import METATYPE_OBJECT as METATYPE_NYSEMEVENT
from naaya.content.semide.project.semproject_item import METATYPE_OBJECT as METATYPE_NYSEMPROJECT

from Products.NaayaCore.PortletsTool.HTMLPortlet import addHTMLPortlet
from Products.NaayaCore.SyndicationTool.RemoteChannel import manage_addRemoteChannel
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent
from naaya.core import submitter

#module constants

METATYPE_OBJECT =       'Naaya Country Folder'
LABEL_OBJECT =          'Country Folder'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Country objects'

OBJECT_FORMS =          ['country_add', 'country_edit', 'country_index', 'country_editportlet']
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
    'smallflag':            (0, '', ''),
    'del_smallflag':        (0, '', ''),
    'link_ins':             (0, '', ''),
    'link_doc':             (0, '', ''),
    'link_train':           (0, '', ''),
    'link_rd':              (0, '', ''),
    'link_data':            (0, '', ''),
    'legislation_feed_url': (0, '', ''),
    'project_feed_url':     (0, '', ''),
    'tooltip':              (0, '', ''),
    'lang':                 (0, '', '')
}

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'nfp_label':            dict(sortorder=100, widget_type='String', label='NFP short label', localized=True),
    'nfp_url':              dict(sortorder=110, widget_type='String', label='NFP URL', default='http://', localized=True),
    'link_ins':             dict(sortorder=120, widget_type='String', label='Institutions URL', default='http://', localized=True),
    'link_doc':             dict(sortorder=130, widget_type='String', label='Documentation URL', default='http://', localized=True),
    'link_train':           dict(sortorder=140, widget_type='String', label='Training URL', default='http://', localized=True),
    'link_rd':              dict(sortorder=150, widget_type='String', label='Research & Development URL', default='http://', localized=True),
    'link_data':            dict(sortorder=160, widget_type='String', label='Data management URL', default='http://', localized=True),
    'legislation_feed_url': dict(sortorder=170, widget_type='String', label='Legislation on Water RSS feed URL', default='http://'),
    'project_feed_url':     dict(sortorder=180, widget_type='String', label='Project Water RSS feed URL', default='http://'),
})
DEFAULT_SCHEMA['sortorder'].update(visible=True)

config = {
    'product': 'NaayaContent',
    'module': 'NyCountry',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_OBJECT,
    'label': LABEL_OBJECT,
    'permission': PERMISSION_ADD_OBJECT,
    'forms': OBJECT_FORMS,
    'add_form': OBJECT_ADD_FORM,
    'description': DESCRIPTION_OBJECT,
    'default_schema': DEFAULT_SCHEMA,
    'properties': PROPERTIES_OBJECT,
    'schema_name': 'NyCountry',
    '_module': sys.modules[__name__],
    'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyCountry.gif'),
    '_misc': {
        'NyCountry.gif': ImageFile('www/NyCountry.gif', globals()),
        'NyCountry_marked.gif': ImageFile('www/NyCountry_marked.gif', globals()),
    }
}

manage_addNyCountry_html = PageTemplateFile('zpt/country_manage_add', globals())
manage_addNyCountry_html.kind = METATYPE_OBJECT
manage_addNyCountry_html.action = 'addNyCountry'

def country_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyCountry', 'form_helper': form_helper}, 'country_add')

def _create_NyCountry_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix=PREFIX_OBJECT)
    ob = NyCountry(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyCountry(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an object of Country type.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    #process parameters
    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix=PREFIX_OBJECT)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    ob = _create_NyCountry_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/country_add_html' % self.absolute_url())

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()
    ob.updatePropertiesFromGlossary(_lang)

    if 'discussion' in schema_raw_data and schema_raw_data['discussion']: ob.open_for_comments()

    #set smallflag from URL or from file upload
    if 'flag_file' in schema_raw_data and schema_raw_data['flag_file']:
        ob.setSmallFlag(schema_raw_data['flag_file'])
    elif 'flag_url' in schema_raw_data and schema_raw_data['flag_url']:
        ob.setSmallFlag(schema_raw_data['flag_url'])

    ob.loadDefaultData(_lang, schema_raw_data.get('legislation_feed_url', ''), schema_raw_data.get('project_feed_url',''))


    self.recatalogNyObject(ob)
    zope.event.notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))

    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)

    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'country_manage_add' or l_referer.find('country_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'country_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/country_add_html' % self.absolute_url())
    return ob.getId()

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

        #Creating object and setting all object properties (taken from Schema)
        ob = _create_NyCountry_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
        for prop in ob._get_schema().listPropNames():
            setattr(ob, prop, '')
        for k, v  in attrs.items():
            setattr(ob, k, v.encode('utf-8'))

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

    default_form_id = 'country_index'

    manage_options = (
        NyFolder.manage_options
    )

    security = ClassSecurityInfo()

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self, lang, legislation_feed_url, project_feed_url):
        """ """
        #load country folder skeleton - default content
        path = os.path.join(Globals.package_home(globals()), 'skel.nyexp')
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
        meta_types = FolderMetaTypes(self).get_values()
        return 'custom_index="%s" maintainer_email="%s" folder_meta_types="%s" smallflag="%s" legislation_feed_url="%s" project_feed_url="%s"' % \
            (self.utXmlEncode(self.compute_custom_index_value()),
                self.utXmlEncode(self.maintainer_email),
                self.utXmlEncode(','.join(meta_types)),
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
        return self.utLinkValue(self.getLocalProperty('link_ins')) or self.utLinkValue(self.getLocalProperty('link_doc')) or \
            self.utLinkValue(self.getLocalProperty('link_train')) or self.utLinkValue(self.getLocalProperty('link_rd')) or \
            self.utLinkValue(self.getLocalProperty('link_data'))

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

    def hasSmallFlag(self):
        return hasattr(self, 'smallflag') and self.smallflag is not None

    def getSmallFlag(self, REQUEST=None):
        """ Return 404 if no flag is found or return the flag"""
        if self.hasSmallFlag():
            if hasattr(self, 'smallflag_type'):
                REQUEST.RESPONSE.setHeader('Content-Type', self.smallflag_type)
            return self.smallflag
        else:
            return REQUEST.RESPONSE.setStatus(404);

    def setSmallFlag(self, source = None, content_type = None):
        """
        source can be:
            URL (String)
            ZPublisher.HTTPRequest.FileUpload
            Encoded Image (String) with content_type set
        """
        self.smallflag = None
        self.smallflag_type = None

        if isinstance(source, str) and not content_type: #this is an URL so get image from web
            l_data, l_ctype = self.grabFromUrl(source)
            if 'image' in l_ctype and l_data is not None:
                self.smallflag = l_data
                self.smallflag_type = l_ctype
        else:
            if hasattr(source, 'filename'):
                self.smallflag = source.read()
                try:
                    self.smallflag_type = source.headers.getheader('Content-Type')
                except:
                    self.smallflag_type = None
            else:
                self.smallflag = source
                self.smallflag_type = type
        self._p_changed = 1

    def delSmallFlag(self):
        """ """
        self.smallflag = None
        self.smallflag_type = None
        self._p_changed = 1
    def _portlets_from_list(self, l=[]):
        return filter(lambda x: x is not None, map(self.getPortletsTool()._getOb, l, (None,)*len(l)))
    def get_left_portlets_objects(self):
        """get the left portlets objects"""
        return self._portlets_from_list(['portlet_country_left'])

    def get_right_portlets_objects(self):
        """get the right portlets objects"""
        l = []
        t = self.getPortletsTool()

        p = self.get_portlet_indicators()
        if p is not None: l.append(p)
        p = self.get_portlet_reports()
        if p is not None: l.append(p)
        return l + self._portlets_from_list(['portlet_country_news', 'portlet_country_events', 'portlet_country_projects'])

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject(): #Check if user can edit the content
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            return REQUEST.RESPONSE.redirect('%s/manage_edit_html?lang=%s' % (self.absolute_url(), _lang))

        self.updatePropertiesFromGlossary(_lang)
        if schema_raw_data.get('discussion', None):
            self.open_for_comments()
        else:
            self.close_for_comments()

        approved = schema_raw_data.get('approved', 0)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)

        if schema_raw_data.get('del_smallflag', ''): self.delSmallFlag()
        elif 'flag_file' in schema_raw_data and schema_raw_data['flag_file']:
            self.setSmallFlag(schema_raw_data['flag_file'])
        elif 'flag_url' in schema_raw_data and schema_raw_data['flag_url']:
            self.setSmallFlag(schema_raw_data['flag_url'])

        self.custom_index = schema_raw_data.get('custom_index', '')
        self._p_changed = 1
        self.recatalogNyObject(self)

        #update remote channels feeds
        self.get_rc_legislation().set_new_feed_url(schema_raw_data.get('legislation_feed_url', ''))
        self.get_rc_project().set_new_feed_url(schema_raw_data.get('project_feed_url', ''))
        # Create log
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        zope.event.notify(NyContentObjectEditEvent(self, contributor))

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ Edit """
        if not self.checkPermissionEditObject(): #Check if user can edit the content
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is None:
                raise ValueError(form_errors.popitem()[1]) # pick a random error
            else:
                import transaction; transaction.abort() # because we already called _crete_NyZzz_object
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

        self.updatePropertiesFromGlossary(_lang)

        if schema_raw_data.get('discussion', None):
            self.open_for_comments()
        else:
            self.close_for_comments()
        #update remote channels feeds
        self.get_rc_legislation().set_new_feed_url(schema_raw_data.get('legislation_feed_url', ''))
        self.get_rc_project().set_new_feed_url(schema_raw_data.get('project_feed_url', ''))

        if schema_raw_data.get('del_smallflag', ''): self.delSmallFlag()
        elif 'flag_file' in schema_raw_data and schema_raw_data['flag_file']:
            self.setSmallFlag(schema_raw_data['flag_file'])
        elif 'flag_url' in schema_raw_data and schema_raw_data['flag_url']:
            self.setSmallFlag(schema_raw_data['flag_url'])

        self._p_changed = 1
        self.recatalogNyObject(self)

        # Create log
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        zope.event.notify(NyContentObjectEditEvent(self, contributor))
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'update_legislation_feed')
    def update_legislation_feed(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        channel = self.get_rc_legislation()
        channel.harvest_feed()
        if REQUEST:
            if channel.get_feed_bozo_exception() is not None: self.setSessionErrorsTrans([channel.get_feed_bozo_exception()])
            else: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/legislation_water/' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'update_project_feed')
    def update_project_feed(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        channel = self.get_rc_project()
        channel.harvest_feed()
        if REQUEST:
            if channel.get_feed_bozo_exception() is not None: self.setSessionErrorsTrans([channel.get_feed_bozo_exception()])
            else: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/editportlet_html?id=%s' % (self.absolute_url(), id))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/country_manage_edit', globals())

    #public pages
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'country_edit')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'editportlet_html')
    def editportlet_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'country_editportlet')

Globals.InitializeClass(NyCountry)

#Custom page templates
NaayaPageTemplateFile('zpt/country_contacts', globals(),
                      'country_contacts')
NaayaPageTemplateFile('zpt/country_legislation_water', globals(),
                      'country_legislation_water')
NaayaPageTemplateFile('zpt/country_project_water', globals(),
                      'country_project_water')

config.update({
    'constructors': (manage_addNyCountry_html, addNyCountry),
    'folder_constructors': [
            ('manage_addNyCountry_html', manage_addNyCountry_html),
            ('country_add_html', country_add_html),
            ('addNyCountry', addNyCountry),
            ('import_NyCountry', importNyCountry),
        ],
    'add_method': addNyCountry,
    'validation': issubclass(NyCountry, NyValidation),
    '_class': NyCountry,
})

def get_config():
    return config
