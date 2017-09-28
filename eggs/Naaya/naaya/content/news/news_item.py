from copy import deepcopy
import os
import sys

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from DateTime import DateTime
from zope.interface import implements

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.managers.utils import slugify, uniqueId, get_nsmap
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session

from interfaces import INyNews
from permissions import PERMISSION_ADD_NEWS

from lxml import etree
from lxml.builder import ElementMaker

#pluggable type metadata
PROPERTIES_OBJECT = {
    'id':               (0, '', ''),
    'title':            (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':      (0, '', ''),
    'coverage':         (0, '', ''),
    'keywords':         (0, '', ''),
    'sortorder':        (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':      (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':       (0, '', ''),
    'details':          (0, '', ''),
    'expirationdate':   (0, MUST_BE_DATETIME, 'The Expires field must contain a valid date.'),
    'topitem':          (0, '', ''),
    'smallpicture':     (0, '', ''),
    'del_smallpicture': (0, '', ''),
    'bigpicture':       (0, '', ''),
    'del_bigpicture':   (0, '', ''),
    'resourceurl':      (0, '', ''),
    'source':           (0, '', ''),
    'lang':             (0, '', '')
}
DEFAULT_SCHEMA = {
    'details':          dict(sortorder=100, widget_type='TextArea', label='Details (HTML)', localized=True, tinymce=True),
    'expirationdate':   dict(sortorder=110, widget_type='Date',     label='Expiration date', data_type='date'),
    'topitem':          dict(sortorder=120, widget_type='Checkbox', label='Top item', data_type='int'),
    'resourceurl':      dict(sortorder=130, widget_type='URL',      label='Concerned URL'),
    'source':           dict(sortorder=140, widget_type='String',   label='Source', localized=True),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['description'].update(help_text='Keep this description short, about 50 words. Use the <strong>Details</strong> field below to add more information.')

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'news_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya News',
        'label': 'News',
        'permission': PERMISSION_ADD_NEWS,
        'forms': ['news_add', 'news_edit', 'news_index'],
        'add_form': 'news_add_html',
        'description': 'This is Naaya News type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyNews',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'news.gif'),
        '_misc': {
                'NyNews.gif': ImageFile('www/news.gif', globals()),
                'NyNews_marked.gif': ImageFile('www/news_marked.gif', globals()),
            },
    }

def news_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyNews',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'news_add')

def _create_NyNews_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'news', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyNews(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyNews(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a News type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('details', '')
    schema_raw_data.setdefault('resourceurl', '')
    schema_raw_data.setdefault('source', '')
    schema_raw_data.setdefault('topitem', '')
    _smallpicture = schema_raw_data.pop('smallpicture', '')
    _bigpicture = schema_raw_data.pop('bigpicture', '')

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or 'news',
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyNews_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/news_add_html' % self.absolute_url())
            return

    ob.setSmallPicture(_smallpicture)
    ob.setBigPicture(_bigpicture)

    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'news_manage_add' or l_referer.find('news_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'news_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

    return ob.getId()

def importNyNews(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyNews_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.expirationdate = self.utConvertDateTimeObjToString(self.utGetDate(attrs['expirationdate'].encode('utf-8')))
            ob.topitem = abs(int(attrs['topitem'].encode('utf-8')))
            ob.smallpicture = self.utBase64Decode(attrs['smallpicture'].encode('utf-8'))
            ob.bigpicture = self.utBase64Decode(attrs['bigpicture'].encode('utf-8'))
            ob.resourceurl = attrs['resourceurl'].encode('utf-8')

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class news_item(Implicit, NyContentData):
    """ """
    smallpicture = None
    bigpicture = None

    def setSmallPicture(self, p_picture):
        """
        Upload the small picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.smallpicture = l_read
                        self._p_changed = 1
            else:
                self.smallpicture = p_picture
                self._p_changed = 1

    def setBigPicture(self, p_picture):
        """
        Upload the big picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.bigpicture = l_read
                        self._p_changed = 1
            else:
                self.bigpicture = p_picture
                self._p_changed = 1

    def delSmallPicture(self):
        """
        Delete the small picture.
        """
        self.smallpicture = None
        self._p_changed = 1

    def delBigPicture(self):
        """
        Delete the big picture.
        """
        self.bigpicture = None
        self._p_changed = 1

class NyNews(news_item, NyAttributes, NyItem, NyCheckControl, NyContentType):
    """ """

    implements(INyNews)

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyNews.gif'
    icon_marked = 'misc_/NaayaContent/NyNews_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        news_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('details', lang), self.getLocalProperty('source', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'expirationdate="%s" topitem="%s" resourceurl="%s" smallpicture="%s" bigpicture="%s"' % \
            (self.utXmlEncode(self.utNoneToEmpty(self.expirationdate)),
                self.utXmlEncode(self.topitem),
                self.utXmlEncode(self.resourceurl),
                self.utBase64Encode(self.utNoneToEmpty(self.smallpicture)),
                self.utBase64Encode(self.utNoneToEmpty(self.bigpicture)))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<details lang="%s"><![CDATA[%s]]></details>' % (l, self.utToUtf8(self.getLocalProperty('details', l))))
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        item = rss_item_for_object(self, lang)
        syndication_tool = self.getSyndicationTool()
        namespaces = syndication_tool.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        dc_namespace = nsmap['dc']
        Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
        the_rest = Dc.root(
            Dc.type('Text'),
            Dc.format('text'),
            Dc.source(self.source),
            Dc.creator(l_site.creator),
            Dc.publisher(l_site.publisher)
            )
        item.extend(the_rest)
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    def getSmallPicture(self, version=None, REQUEST=None):
        """ """
        if version is None: return self.smallpicture
        else:
            if self.checkout: return self.version.smallpicture
            else: return self.smallpicture

    def getBigPicture(self, version=None, REQUEST=None):
        """ """
        if version is None: return self.bigpicture
        else:
            if self.checkout: return self.version.bigpicture
            else: return self.bigpicture

    def hasSmallPicture(self, version=None):
        if version is None: return self.smallpicture is not None
        else:
            if self.checkout: return self.version.smallpicture is not None
            else: return self.smallpicture is not None

    def hasBigPicture(self, version=None):
        if version is None: return self.bigpicture is not None
        else:
            if self.checkout: return self.version.bigpicture is not None
            else: return self.bigpicture is not None

    #zmi actions
    def manage_FTPget(self):
        """ Return body for ftp """
        return self.details

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))
        _smallpicture = schema_raw_data.pop('smallpicture', '')
        _del_smallpicture = schema_raw_data.pop('del_smallpicture', '')
        _bigpicture = schema_raw_data.pop('bigpicture', '')
        _del_bigpicture = schema_raw_data.pop('del_bigpicture', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        if _del_smallpicture != '': self.delSmallPicture()
        else: self.setSmallPicture(_smallpicture)
        if _del_bigpicture != '': self.delBigPicture()
        else: self.setBigPicture(_bigpicture)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if (not self.checkPermissionEditObject()) or (
            self.checkout_user != user):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.copy_naaya_properties_from(self.version)
        self.smallpicture = self.version.smallpicture
        self.bigpicture = self.version.bigpicture
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        notify(NyContentObjectEditEvent(self, user))
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
        self.version = news_item()
        self.version.copy_naaya_properties_from(self)
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            obj = self.version
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        else:
            obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)
        _smallpicture = schema_raw_data.pop('smallpicture', '')
        _del_smallpicture = schema_raw_data.pop('del_smallpicture', '')
        _bigpicture = schema_raw_data.pop('bigpicture', '')
        _del_bigpicture = schema_raw_data.pop('del_bigpicture', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            if _del_smallpicture != '': self.delSmallPicture()
            else: self.setSmallPicture(_smallpicture)
            if _del_bigpicture != '': self.delBigPicture()
            else: self.setBigPicture(_bigpicture)
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                self.setSession('del_smallpicture', _del_smallpicture)
                self.setSession('del_bigpicture', _del_bigpicture)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'change_topitem_status')
    def change_topitem_status(self, REQUEST=None):
        """ show/hide event on the front page """
        if self.topitem:
            self.topitem = False
        else:
            self.topitem = True

        self.recatalogNyObject(self)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    @property
    def has_expired(self):
        if not self.expirationdate:
            return
        return (DateTime() - 1).greaterThan(self.expirationdate)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/news_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        self.notify_access_event(REQUEST)
        return self.getFormsTool().getContent({'here': self}, 'news_index')

    security.declareProtected(view, 'picture_html')
    def picture_html(self, REQUEST=None, RESPONSE=None):
        """ """
        REQUEST.RESPONSE.setHeader('content-type', 'text/html')
        return '<img src="getBigPicture" alt="" />'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'news_edit')

InitializeClass(NyNews)

manage_addNyNews_html = PageTemplateFile('zpt/news_manage_add', globals())
manage_addNyNews_html.kind = config['meta_type']
manage_addNyNews_html.action = 'addNyNews'

#Custom folder index for news
NaayaPageTemplateFile('zpt/news_folder_index', globals(), 'news_folder_index')

config.update({
    'constructors': (manage_addNyNews_html, addNyNews),
    'folder_constructors': [
            # NyFolder.manage_addNyNews_html = manage_addNyNews_html
            ('manage_addNyNews_html', manage_addNyNews_html),
            ('news_add_html', news_add_html),
            ('addNyNews', addNyNews),
            ('import_news_item', importNyNews),
        ],
    'add_method': addNyNews,
    'validation': issubclass(NyNews, NyValidation),
    '_class': NyNews,
})

def get_config():
    return config
