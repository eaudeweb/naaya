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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright   European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Anton Cupcea, Eau de Web
# Cornel Nitu, Eau de Web
# Miruna Badescu, Eau de Web
# Dragos Chirila
# Alex Morega, Eau de Web
# David Batranu, Eau de Web

#Python imports
from copy import deepcopy
import os
import sys

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Products
from Acquisition import Implicit
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData

#module constants
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'body':         (0, '', ''),
    'topitem':      (0, '', ''),
    'resourceurl':  (0, '', ''),
    'source':       (0, '', ''),
    'frontpicture': (0, '', ''),
    'lang':         (0, '', '')
}
DEFAULT_SCHEMA = {
    'body':         dict(sortorder=100, widget_type='TextArea', label='Body (HTML)', localized=True, tinymce=True),
    'topitem':      dict(sortorder=110, widget_type='Checkbox', label='Top item', data_type='int'),
    'resourceurl':  dict(sortorder=120, widget_type='String',   label='Concerned URL'),
    'source':       dict(sortorder=130, widget_type='String',   label='Source'),
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'story_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Story',
        'label': 'Story',
        'permission': 'Naaya - Add Naaya Story objects',
        'forms': ['story_add', 'story_edit', 'story_index'],
        'add_form': 'story_add',
        'description': 'This is Naaya Story type.',
        'properties': PROPERTIES_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyStory',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'story.gif'),
        '_misc': {
                'NyStory.gif': ImageFile('www/story.gif', globals()),
                'NyStory_marked.gif': ImageFile('www/story_marked.gif', globals()),
            },
    }

def story_add(self, REQUEST=None, RESPONSE=None):
    """ """
    id = 'story' + self.utGenRandomId(6)
    self.addNyStory(id)
    if REQUEST: REQUEST.RESPONSE.redirect('%s/add_html' % self._getOb(id).absolute_url())

def _create_NyStory_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyStory(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyStory(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Story type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    schema_raw_data.setdefault('body', '')
    schema_raw_data.setdefault('resourceurl', '')
    schema_raw_data.setdefault('source', '')
    schema_raw_data.setdefault('topitem', '')
    _frontpicture = schema_raw_data.pop('frontpicture', '')

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = 'story' + self.utGenRandomId(5)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyStory_object(self, id, contributor)
    ob._setLocalPropValue('title', _lang, '')

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate, _all_values=False)
    if form_errors:
        raise ValueError(form_errors.popitem()[1]) # pick a random error

    ob.setFrontPicture(_frontpicture)

    if kwargs.has_key('submitted'): ob.submitThis()
    if self.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        if REQUEST.has_key('submitted'): ob.submitThis()
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'story_manage_add' or l_referer.find('story_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'story_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    return ob.getId()

def importNyStory(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyStory_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))
            ob.topitem = abs(int(attrs['topitem'].encode('utf-8')))
            ob.resourceurl = attrs['resourceurl'].encode('utf-8')
            ob.frontpicture = self.utBase64Decode(attrs['frontpicture'].encode('utf-8'))

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.submitThis()
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)
        for object in objects:
            self.import_data_custom(ob, object)

class story_item(Implicit, NyContentData):
    """ """
    frontpicture = None

    def setFrontPicture(self, p_picture):
        """
        Upload the front page picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.frontpicture = l_read
                        self._p_changed = 1
            else:
                self.frontpicture = p_picture
                self._p_changed = 1

    def delFrontPicture(self):
        """
        Delete the front page picture.
        """
        self.frontpicture = None
        self._p_changed = 1

class NyStory(story_item, NyAttributes, NyContainer, NyCheckControl, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyStory.py'
    icon_marked = 'misc_/NaayaContent/NyStory_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],) + story_item.manage_options
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        story_item.__init__(self)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('body', lang), self.getLocalProperty('source', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'topitem="%s" resourceurl="%s" frontpicture="%s"' % \
            (self.utXmlEncode(self.topitem), self.utXmlEncode(self.resourceurl), self.utBase64Encode(self.utNoneToEmpty(self.frontpicture)))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<body lang="%s"><![CDATA[%s]]></body>' % (l, self.utToUtf8(self.getLocalProperty('body', l))))
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
        for i in self.getUploadedImages():
            ra('<img param="0" id="%s" content="%s" />' % \
                (self.utXmlEncode(i.id()), self.utXmlEncode(self.utBase64Encode(str(i.data)))))
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

    def getFrontPicture(self, version=None, REQUEST=None):
        """ """
        if version is None: return self.frontpicture
        else:
            if self.checkout: return self.version.frontpicture
            else: return self.frontpicture

    def hasFrontPicture(self, version=None):
        if version is None: return self.frontpicture is not None
        else:
            if self.checkout: return self.version.frontpicture is not None
            else: return self.frontpicture is not None

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
        _frontpicture = schema_raw_data.pop('frontpicture', '')
        _del_frontpicture = schema_raw_data.pop('del_frontpicture', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        if _del_frontpicture != '': self.delFrontPicture()
        else: self.setFrontPicture(_frontpicture)
        self._p_changed = 1
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'submitThis')
    def submit_this(self, REQUEST=None):
        """ """
        self.submitThis()
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(config['permission'], 'process_add')
    def process_add(self, REQUEST, **kwargs):
        """ """
        schema_raw_data = dict(REQUEST.form)
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _frontpicture = schema_raw_data.pop('frontpicture', '')
        _contact_word = schema_raw_data.get('contact_word', '')

        id = self.utGenObjectId(schema_raw_data.get('title', ''))

        parent = self.getParentNode()
        #verify if the object already exists
        try:
            ob = parent._getOb(id)
            id = '%s-%s' % (id, self.utGenRandomId(5))
        except AttributeError:
            pass

        schema_raw_data['title'] = schema_raw_data['title'].replace(self.id, id)
        schema_raw_data['description'] = schema_raw_data['description'].replace(self.id, id)
        schema_raw_data['body'] = schema_raw_data['body'].replace(self.id, id)

        #check mandatory fiels
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        #check Captcha/reCaptcha
        if not self.checkPermissionSkipCaptcha():
            captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
            if captcha_validator:
                form_errors['captcha'] = captcha_validator

        if not form_errors:
            parent.manage_renameObjects([self.id], [id])
            if self.glCheckPermissionPublishObjects():
                approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
            else:
                approved, approved_by = 0, None

            self.setFrontPicture(_frontpicture)
            self.approveThis(approved, approved_by)
            self.submitThis()
            if self.discussion: self.open_for_comments()
            self.recatalogNyObject(self)
            notify(NyContentObjectAddEvent(self, self.contributor, schema_raw_data))
            self.setSession('referer', self.getParentNode().absolute_url())
            return self.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.getParentNode().absolute_url())
        else:
            l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
            self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/add_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.copy_naaya_properties_from(self.version)
        self.frontpicture = self.version.frontpicture
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
        self.version = story_item()
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
        _frontpicture = schema_raw_data.pop('frontpicture', '')
        _del_frontpicture = schema_raw_data.pop('del_frontpicture', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            if _del_frontpicture != '': obj.delFrontPicture()
            else: obj.setFrontPicture(_frontpicture)
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
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                self.setSession('del_frontpicture', _del_frontpicture)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/story_manage_edit', globals())

    #site pages
    security.declareProtected(config['permission'], 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'story_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'story_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'story_edit')

InitializeClass(NyStory)

manage_addNyStory_html = PageTemplateFile('zpt/story_manage_add', globals())
manage_addNyStory_html.kind = config['meta_type']
manage_addNyStory_html.action = 'addNyStory'
config.update({
    'constructors': (manage_addNyStory_html, addNyStory),
    'folder_constructors': [
            # NyFolder.manage_addNyStory_html = manage_addNyStory_html
            ('manage_addNyStory_html', manage_addNyStory_html),
            ('story_add', story_add),
            ('addNyStory', addNyStory),
            ('import_story_item', importNyStory),
        ],
    'add_method': addNyStory,
    'validation': issubclass(NyStory, NyValidation),
    '_class': NyStory,
})

def get_config():
    return config
