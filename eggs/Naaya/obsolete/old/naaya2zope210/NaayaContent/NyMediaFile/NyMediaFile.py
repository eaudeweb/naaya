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
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Alin Voinea, Eau de Web
# Alex Morega, Eau de Web

#Python imports
from copy import deepcopy

#Zope imports
import zLOG
from OFS.Image import File, cookId
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Products

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from mediafile_item import mediafile_item

from converters.MediaConverter import \
     media2flv, \
     can_convert, \
     get_conversion_errors

from parsers import DEFAULT_PARSER as SubtitleParser

#module constants
METATYPE_OBJECT = 'Naaya Media File'
LABEL_OBJECT = 'Media File'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Media File objects'
OBJECT_FORMS = ['mediafile_add', 'mediafile_edit', 'mediafile_index', 'mediafile_subtitle']
OBJECT_CONSTRUCTORS = ['manage_addNyMediaFile_html', 'mediafile_add_html', 'addNyMediaFile', 'importNyMediaFile']
OBJECT_ADD_FORM = 'mediafile_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Media File type.'
PREFIX_OBJECT = 'media'
PROPERTIES_OBJECT = {
    'id':           (0, '', ''),
    'title':        (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':  (0, '', ''),
    'coverage':     (0, '', ''),
    'keywords':     (0, '', ''),
    'sortorder':    (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':  (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':   (0, '', ''),
    'file':         (1, '', ''),
    'lang':         (0, '', ''),
    'subtitle':     (0, '', ''),
}
DEFAULT_SCHEMA = {
    # add NyMediaFile-specific properties here
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# If converters installed file must be video, otherwise must be flash video (flv)

ffmpeg_available = can_convert() and NyFSContainer.is_ext
if ffmpeg_available:
    PROPERTIES_OBJECT["file"] = (1, MUST_BE_VIDEOFILE, "The file must be a valid video file (e.g. .avi, .mpg, .mp4, etc.)")
else:
    zLOG.LOG("NyMediaFile", zLOG.WARNING,
             "Video conversion will not be supported.")
    PROPERTIES_OBJECT["file"] = (1, MUST_BE_FLVFILE, "The file must be a valid flash video file (.flv)")

FLV_HEADERS = ["application/x-flash-video", "video/x-flv"]

manage_addNyMediaFile_html = PageTemplateFile('zpt/mediafile_manage_add', globals())
manage_addNyMediaFile_html.kind = METATYPE_OBJECT
manage_addNyMediaFile_html.action = 'addNyMediaFile'

def mediafile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyMediaFile', 'form_helper': form_helper}, 'mediafile_add')

def _create_NyMediaFile_object(parent, id, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyMediaFile(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def _check_video_file(the_file):
    errors = []
    if ffmpeg_available:
        # TODO: check if our file is a valid video file!
        pass
    else:
        if not the_file or the_file.headers.get("content-type", "") not in FLV_HEADERS:
            errors += ['The file must be a valid flash video file (.flv)']
    return errors

def addNyMediaFile(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a File type of object.
    """


    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _file = schema_raw_data.pop('file', '')
    _subtitle = schema_raw_data.pop('subtitle', '')
    _skip_videofile_check = schema_raw_data.pop('_skip_videofile_check', False)
    _contact_word = schema_raw_data.get('contact_word', '')
    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(schema_raw_data.get('title', ''))
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(5)

    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyMediaFile_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator


    video_errors = _check_video_file(_file)
    if video_errors and not _skip_videofile_check:
        form_errors['mediafile'] = video_errors

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/mediafile_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    ob.handleMediaUpload(_file)
    ob._setLocalPropValue('subtitle', _lang, _subtitle)

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    if _send_notifications:
        self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'mediafile_manage_add' or l_referer.find('mediafile_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'mediafile_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()

def importNyMediaFile(self, param, id, attrs, content, properties, discussion, objects):
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

            ob = _create_NyMediaFile_object(self, id, self.utEmptyToNone(attrs['contributor'].encode('utf-8')))
            ob.sortorder = attrs['sortorder'].encode('utf-8')
            ob.discussion = abs(int(attrs['discussion'].encode('utf-8')))

            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.checkThis(attrs['validation_status'].encode('utf-8'),
                attrs['validation_comment'].encode('utf-8'),
                attrs['validation_by'].encode('utf-8'),
                attrs['validation_date'].encode('utf-8'))
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)
        for object in objects:
            self.import_data_custom(ob, object)

class NyMediaFile(mediafile_item, NyAttributes, NyFSContainer, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyMediaFile.gif'
    icon_marked = 'misc_/NaayaContent/NyMediaFile_marked.gif'
    player = 'misc_/NaayaContent/EdWideoPlayer.swf'

    def manage_options(self):
        """ """
        l_options = (NyFSContainer.manage_options[0],)
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += mediafile_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyFSContainer.manage_options[3:8]
        return l_options

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ["ExtFile", "File"]
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    def __init__(self, id, contributor):
        """ """
        self.subobj_meta_type = NyFSContainer.is_ext and "ExtFile" or "File"
        self.id = id
        mediafile_item.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyFSContainer.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'validation_status="%s" validation_date="%s" validation_by="%s" validation_comment="%s"' % \
            (self.utXmlEncode(self.validation_status),
                self.utXmlEncode(self.validation_date),
                self.utXmlEncode(self.validation_by),
                self.utXmlEncode(self.validation_comment))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for i in self.getMediaObjects():
            ra('<file param="0" id="%s" content="%s" />' % \
                (self.utXmlEncode(i.id), self.utXmlEncode(self.utBase64Encode(str(i.get_data())))))
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
        ra('<dc:format>application</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        ra('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    def getSingleMediaObject(self):
        """
        Returns the B{SINGLE} media file if exists.
        """
        l = self.objectValues(self.subobj_meta_type)
        if len(l)>0:
            return l[0]
        else:
            return None

    def getSingleMediaId(self):
        """ Return the B{SINGLE} media id if exists.
        """
        media = self.getSingleMediaObject()
        return media and media.getId() or ""

    def mediaReady(self):
        """ Check if media is ready
        """
        media = self.getSingleMediaObject()
        if media:
            return self.isReady(media.getId())
        return False

    def mediaBroken(self):
        """ Check if media conversion finished and no error occured.
        """
        if self.mediaReady():
            return ""

        media = self.getSingleMediaObject()
        if not media:
            return "File broken."

        if not self.is_ext:
            #TODO: Handle ZODB files
            return ""

        mpath = media.get_filename()
        return get_conversion_errors(mpath)

    def getMediaObjects(self):
        """
        Returns the list of media files, B{File} objects.
        """
        meta_types = getattr(self, 'subobj_meta_type', None)
        return self.objectValues(meta_types)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        _subtitle = schema_raw_data.pop('subtitle', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        self._setLocalPropValue('subtitle', _lang, _subtitle)

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        self._p_changed = 1
        if self.discussion: self.open_for_comments()
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
        self.handleMediaUpload(file)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_upload')
    def manage_upload(self):
        """ """
        raise EXCEPTION_NOTACCESIBLE, 'manage_upload'

    #site actions
    def handleMediaUpload(self, file):
        """
        Handle upload of a media file. A B{File} object will be created inside
        the B{NyMediafile} object.
        """
        if file == '':
            return
        if not hasattr(file, 'filename'):
            return
        if file.filename == '':
            return

        self.manage_delObjects(self.objectIds())

        ctype = file.headers.get("content-type")
        filename = file.filename.split(".")
        file.filename = filename[0] + ".flv"
        file.headers["content-type"] = "application/x-flash-video"
        mid = self.manage_addFile('', file)
        self._processFile(mid, ctype)

    security.declarePrivate("_processFile")
    def _processFile(self, mid, ctype):
        """ Apply media converters to self subobject with given id (mid) with
        original content-type ctype.
        """
        if self.is_ext:
            self._processExtFile(mid, ctype)
        else:
            self._processZODBFile(mid, ctype)

    security.declarePrivate("_processZODBFile")
    def _processZODBFile(self, mid, ctype):
        """ Apply media converters to self subobject with given id (mid) which
        is stored in Data.fs, with original content-type ctype
        """
        # TODO: handle conversion of ZODB files
        return

    security.declarePrivate("_processExtFile")
    def _processExtFile(self, mid, ctype):
        """ Apply media converters to self subobject with given id (mid) which
        is stored outside Data.fs, with original content-type ctype.
        """
        media = self._getOb(mid)
        mid = media.get_filename()
        return media2flv(mid, ".tmp")

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self.copy_naaya_properties_from(self.version)
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
        self.version = mediafile_item()
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

        _subtitle = schema_raw_data.pop('subtitle', '')
        _subtitle_file = schema_raw_data.pop('subtitle_file', None)
        _source = schema_raw_data.pop('source', None)
        _file = schema_raw_data.pop('file', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        # TODO: check if video file is good video file

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _subtitle_file:
            _subtitle = _subtitle_file.read()
        self._setLocalPropValue('subtitle', _lang, _subtitle)
        if _source:
            self.saveUpload(file=_file, lang=_lang)

        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, file='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        if lang is None: lang = self.gl_get_selected_language()
        self.handleMediaUpload(file)
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declarePrivate('switch_content_to_language')
    def switch_content_to_language(self, old_lang, new_lang):
        super(NyMediaFile, self).switch_content_to_language(old_lang, new_lang)
        subtitle = self.getLocalProperty('subtitle', old_lang)
        self._setLocalPropValue('subtitle', new_lang, subtitle)
        self._setLocalPropValue('subtitle', old_lang, '')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/mediafile_manage_edit', globals())

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'mediafile_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'mediafile_edit')

    security.declareProtected(view, 'subtitle_xml')
    def subtitle_xml(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'mediafile_subtitle')

    def getSubtitle(self, REQUEST=None, RESPONSE=None):
        """ """
        parser = SubtitleParser(self.subtitle)
        return parser.parse()

    security.declareProtected(view, 'getSize')
    def getSize(self):
        video = self.getSingleMediaObject()
        if not (video and self.is_ext):
            return 0
        return video.get_size()

InitializeClass(NyMediaFile)

