import os
import sys

import zLOG
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

from naaya.content.bfile.NyBlobFile import make_blobfile

from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from naaya.i18n.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaBase.NyBase import rss_item_for_object
from Products.NaayaCore.managers.utils import slugify, uniqueId, get_nsmap
from naaya.core import submitter
from naaya.core.zope2util import abort_transaction_keep_session
from naaya.core.zope2util import ofs_path, launch_job
from naaya.core.utils import force_to_unicode

from lxml import etree
from lxml.builder import ElementMaker

from converters.MediaConverter import \
     media2flv, \
     can_convert, \
     get_conversion_errors

from permissions import PERMISSION_ADD_MEDIA_FILE
from parsers import DEFAULT_PARSER as SubtitleParser

#module constants
DEFAULT_SCHEMA = {
    # add NyMediaFile-specific properties here
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

# If converters installed file must be video, otherwise must be flash video (flv)

ffmpeg_available = can_convert() and NyFSContainer.is_ext
if not ffmpeg_available:
    zLOG.LOG("NyMediaFile", zLOG.WARNING,
             "Video conversion will not be supported.")

FLV_HEADERS = ["application/x-flash-video", "video/x-flv", "video/flv"]
MP3_HEADERS = ["audio/mpeg"]

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'mediafile_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya Media File',
        'label': 'Media File',
        'permission': PERMISSION_ADD_MEDIA_FILE,
        'forms': ['mediafile_add', 'mediafile_edit', 'mediafile_index', 'mediafile_subtitle'],
        'add_form': 'mediafile_add_html',
        'description': 'This is Naaya MediaFile type.',
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyMediaFile',
        '_module': sys.modules[__name__],
        'additional_style': None,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'mediafile.gif'),
        '_misc': {
                'NyMediaFile.gif': ImageFile('www/mediafile.gif', globals()),
                'NyMediaFile_marked.gif': ImageFile('www/mediafile_marked.gif', globals()),
                'EdWideoPlayer.swf': ImageFile('player/EdWideoPlayer.swf', globals()),
                'NyMediaFileLoading.gif': ImageFile('www/mediafile_loading.gif', globals()),
                'NyMediaFileBroken.gif': ImageFile('www/mediafile_broken.gif', globals()),
            },
    }

def mediafile_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyMediaFile',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
    }, 'mediafile_add')

def _create_NyMediaFile_object(parent, id, contributor):
    id = uniqueId(slugify(id or 'mediafile', removelist=[]),
                  lambda x: parent._getOb(x, None) is not None)
    ob = NyMediaFile_extfile(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def _check_media_file(the_file):
    if the_file is None:
        return ['No file was uploaded']
    file_extension = os.path.splitext(getattr(the_file, 'filename', ''))[1]
    if ffmpeg_available:
        # TODO: check if our file is a valid video file!
        return []
    else:
        if not the_file or \
        (the_file.headers.get("content-type", "") not in FLV_HEADERS+MP3_HEADERS \
        and file_extension not in ['.flv', 'mp3']):
            return ['The file must be a valid flash video file (.flv)']
    return []

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

    _file = schema_raw_data.pop('file', None)
    _subtitle = schema_raw_data.pop('subtitle', '')
    _skip_videofile_check = schema_raw_data.pop('_skip_videofile_check', False)

    id = uniqueId(slugify(id or schema_raw_data.get('title', '') or 'mediafile',
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)

    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyMediaFile_object(self, id, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if not _skip_videofile_check:
        video_errors = _check_media_file(_file)
        if video_errors:
            form_errors['mediafile'] = video_errors

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/mediafile_add_html' % self.absolute_url())
            return

    #process parameters
    if self.checkPermissionSkipApproval():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    ob.handleMediaUpload(_file)
    ob._setLocalPropValue('subtitle', _lang, _subtitle)

    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
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
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        else: # undefined state (different referer, called in other context)
            return ob

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

class mediafile_item(Implicit, NyContentData):
    """ """

    subtitle = LocalProperty('subtitle')
    startup_image = None

class NyMediaFile_extfile(mediafile_item, NyAttributes, NyFSContainer, NyCheckControl, NyValidation, NyContentType):
    """ """

    meta_type = config['meta_type']
    meta_label = config['label']
    icon = 'misc_/NaayaContent/NyMediaFile.gif'
    icon_marked = 'misc_/NaayaContent/NyMediaFile_marked.gif'
    player = 'misc_/NaayaContent/EdWideoPlayer.swf'

    def manage_options(self):
        """ """
        l_options = (NyFSContainer.manage_options[0],)
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
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
        item = rss_item_for_object(self, lang)
        syndication_tool = self.getSyndicationTool()
        namespaces = syndication_tool.getNamespaceItemsList()
        nsmap = get_nsmap(namespaces)
        dc_namespace = nsmap['dc']
        Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
        the_rest = Dc.root(
            Dc.type('Text'),
            Dc.format('application'),
            Dc.source(l_site.publisher),
            Dc.creator(l_site.creator),
            Dc.publisher(l_site.publisher)
            )
        item.extend(the_rest)
        return etree.tostring(item, xml_declaration=False, encoding="utf-8")

    def getSingleMediaObject(self):
        """
        Returns the B{SINGLE} media file if exists.
        """
        l = self.objectValues(['ExtFile', 'File'])
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
        return self.objectValues(['ExtFile', 'File'])

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
        filename = os.path.splitext(getattr(file, 'filename', ''))
        if filename[1] == '.mp3':
            self.manage_addFile('', file)
        else:
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
        launch_job(media2flv, self.aq_parent, ofs_path(media))

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
        _startup_image = schema_raw_data.pop('startup_image', '')
        _delete_startup_image = schema_raw_data.pop('delete_startup_image', '')
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
            _subtitle = force_to_unicode(_subtitle_file.read())
        self._setLocalPropValue('subtitle', _lang, _subtitle)
        if _delete_startup_image:
            self.startup_image = None
        if _startup_image:
            self.startup_image = make_blobfile(_startup_image)
        if _source:
            self.saveUpload(file=_file, lang=_lang)

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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
        if self.hasVersion():
            obj = self.version
        else:
            obj = self
        return self.getFormsTool().getContent({'here': obj}, 'mediafile_edit')

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

    security.declareProtected(view, 'get_aspect_ratio')
    def get_aspect_ratio(self, aspect_ratio=1.5):
        video = self.getSingleMediaObject()
        return getattr(video, 'aspect_ratio', aspect_ratio)

    def is_audio(self):
        return '.mp3' == os.path.splitext(self.getSingleMediaId())[1]

InitializeClass(NyMediaFile_extfile)

manage_addNyMediaFile_html = PageTemplateFile('zpt/mediafile_manage_add', globals())
manage_addNyMediaFile_html.kind = config['meta_type']
manage_addNyMediaFile_html.action = 'addNyMediaFile'
config.update({
    'constructors': (manage_addNyMediaFile_html, addNyMediaFile),
    'folder_constructors': [
            # NyFolder.manage_addNyMediaFile_html = manage_addNyMediaFile_html
            ('manage_addNyMediaFile_html', manage_addNyMediaFile_html),
            ('mediafile_add_html', mediafile_add_html),
            ('addNyMediaFile', addNyMediaFile),
            ('import_mediafile_item', importNyMediaFile),
        ],
    'add_method': addNyMediaFile,
    'validation': issubclass(NyMediaFile_extfile, NyValidation),
    '_class': NyMediaFile_extfile,
})

def get_config():
    return config
