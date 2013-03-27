from copy import deepcopy
import os
import sys

from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from zope.interface import implements
from zope.event import notify

from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyNonCheckControl import NyNonCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.managers.utils import make_id

from interfaces import INyYoutube
from permissions import PERMISSION_ADD_YOUTUBE

from gdata.youtube.service import YouTubeService
from gdata.service import RequestError

DEFAULT_SCHEMA = {
    'youtube_id': dict(sortorder=100, widget_type='String',
                label='YouTube ID', required=True),
    'iframe_width': dict(sortorder=110, widget_type='String',
                label='Video width'),
    'iframe_height': dict(sortorder=120, widget_type='String',
                label='Video height'),
    'captions': {'sortorder':130, 'widget_type':'Checkbox', 'data_type':'int',
                   'label':'Show captions in this language', 
                   'default':True, 'localized':True},
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['coverage'].update(visible=False)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaYoutube',
        'module': 'youtube_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Youtube',
        'label': 'YouTube Video',
        'permission': PERMISSION_ADD_YOUTUBE,
        'forms': ['youtube_add', 'youtube_edit', 'youtube_index'],
        'add_form': 'youtube_add_html',
        'description': 'This is Naaya Youtube embedded video.',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyYoutube',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'youtube.png'),
        '_misc': {
                'NyYoutube.png': ImageFile('www/youtube.png', globals()),
                'NyYoutube_marked.png': ImageFile('www/youtube_marked.png', globals()),
            },
    }

def youtube_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyYoutube', 'form_helper': form_helper}, 'youtube_add')

def _create_NyYoutube_object(parent, id, contributor):
    id = make_id(parent, id=id, prefix='youtube')
    ob = NyYoutube(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyYoutube(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Youtube embeded video.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    _contact_word = schema_raw_data.get('contact_word', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix='ep')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyYoutube_object(self, id, contributor)

    if schema_raw_data['iframe_width'] in ['', '0']:
        schema_raw_data['iframe_width'] = 640
    if schema_raw_data['iframe_height'] in ['', '0']:
        schema_raw_data['iframe_height'] = 360

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    try:
        schema_raw_data['iframe_width'] = int(schema_raw_data['iframe_width'])
    except ValueError:
        form_errors['iframe_width'] = ['Integer value required.']
    try:
        schema_raw_data['iframe_height'] = int(schema_raw_data['iframe_height'])
    except ValueError:
        form_errors['iframe_height'] = ['Integer value required.']
    if not schema_raw_data['youtube_id']:
        form_errors['youtube_id'] = ['Youtube Id is mandatory']

    if schema_raw_data['youtube_id']:
        yt_service = YouTubeService()
        try:
            video_info = yt_service.GetYouTubeVideoEntry(video_id=
                                                schema_raw_data['youtube_id'])
        except RequestError:
            form_errors['youtube_id'] = ['Invalid Youtube ID (inexisting video)']

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/youtube_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'youtube_manage_add' or l_referer.find('youtube_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'youtube_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

class NyYoutube(Implicit, NyContentData, NyAttributes, NyItem, NyNonCheckControl, NyValidation, NyContentType):
    """ """

    implements(INyYoutube)

    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NaayaContent/NyYoutube.png'
    icon_marked = 'misc_/NaayaContent/NyYoutube_marked.png'

    manage_options = (
        {'label': 'Properties', 'action': 'manage_edit_html'},
        {'label': 'View', 'action': 'index_html'},
    ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyValidation.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    #zmi actions
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

        if schema_raw_data['iframe_width'] in ['', '0']:
            schema_raw_data['iframe_width'] = 640
        if schema_raw_data['iframe_height'] in ['', '0']:
            schema_raw_data['iframe_height'] = 360

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        try:
            schema_raw_data['iframe_width'] = int(schema_raw_data['iframe_width'])
        except ValueError:
            form_errors['iframe_width'] = ['Integer value required.']
        try:
            schema_raw_data['iframe_height'] = int(schema_raw_data['iframe_height'])
        except ValueError:
            form_errors['iframe_height'] = ['Integer value required.']
        if not schema_raw_data['youtube_id']:
            form_errors['youtube_id'] = ['Youtube Id is mandatory']

        if schema_raw_data['youtube_id']:
            yt_service = YouTubeService()
            try:
                video_info = yt_service.GetYouTubeVideoEntry(video_id=
                                                    schema_raw_data['youtube_id'])
            except RequestError:
                form_errors['youtube_id'] = ['Invalid Youtube ID (inexisting video)']

        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)
        self._p_changed = 1
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)

        if schema_raw_data['iframe_width'] in ['', '0']:
            schema_raw_data['iframe_width'] = 640
        if schema_raw_data['iframe_height'] in ['', '0']:
            schema_raw_data['iframe_height'] = 360

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        try:
            schema_raw_data['iframe_width'] = int(schema_raw_data['iframe_width'])
        except ValueError:
            form_errors['iframe_width'] = ['Integer value required.']
        try:
            schema_raw_data['iframe_height'] = int(schema_raw_data['iframe_height'])
        except ValueError:
            form_errors['iframe_height'] = ['Integer value required.']
        if not schema_raw_data['youtube_id']:
            form_errors['youtube_id'] = ['Youtube Id is mandatory']

        if schema_raw_data['youtube_id']:
            yt_service = YouTubeService()
            try:
                video_info = yt_service.GetYouTubeVideoEntry(video_id=
                                                    schema_raw_data['youtube_id'])
            except RequestError:
                form_errors['youtube_id'] = ['Invalid Youtube ID (inexisting video)']

        if not form_errors:
            if self.discussion: self.open_for_comments()
            else: self.close_for_comments()
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
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/youtube_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'youtube_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'youtube_edit')

InitializeClass(NyYoutube)

manage_addNyYoutube_html = PageTemplateFile('zpt/youtube_manage_add', globals())
manage_addNyYoutube_html.kind = config['meta_type']
manage_addNyYoutube_html.action = 'addNyYoutube'
config.update({
    'constructors': (manage_addNyYoutube_html, addNyYoutube),
    'folder_constructors': [
            ('manage_addNyYoutube_html', manage_addNyYoutube_html),
            ('youtube_add_html', youtube_add_html),
            ('addNyYoutube', addNyYoutube),
        ],
    'add_method': addNyYoutube,
    'validation': issubclass(NyYoutube, NyValidation),
    '_class': NyYoutube,
})

def get_config():
    return config
