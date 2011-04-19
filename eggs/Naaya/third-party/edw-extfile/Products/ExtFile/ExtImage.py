"""ExtImage product module."""
###############################################################################
#
# Copyright (c) 2001 Gregor Heine <mac.gregor@gmx.de>. All rights reserved.
# ExtFile Home: http://www.zope.org/Members/MacGregor/ExtFile/index_html
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission
#
# Disclaimer
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  In accordance with the license provided for by the software upon
#  which some of the source code has been derived or used, the following
#  acknowledgement is hereby provided :
#
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
#
###############################################################################

__doc__ = """ExtImage product module.
    The ExtImage-Product works like the Zope Image-product, but stores the
    uploaded image externally in a repository-direcory. It creates a preview
    of the image (requires PIL)."""

__version__='2.0.2'

from Globals import HTMLFile, MessageDialog, InitializeClass
from AccessControl import ClassSecurityInfo
from webdav.Lockable import ResourceLockedError
import urllib, os, string
from os.path import join, isfile
from tempfile import TemporaryFile
from zExceptions import Redirect
from OFS.Image import getImageInfo
from OFS.Image import Pdata
from Acquisition import aq_base
from DocumentTemplate.html_quote import html_quote

try:
    from webdav.interfaces import IWriteLock
except ImportError: #< zope2.12
    from webdav.WriteLockInterface import WriteLockInterface as IWriteLock
from zope import interface
from interfaces import IExtImage
from zope import event
from interfaces import ExtImageUpdatedEvent

from Products.ExtFile.ExtFile import ExtFile
from Products.ExtFile.ExtFile import normalize_id
from Products.ExtFile.ExtFile import pdata
from Products.ExtFile.ExtFile import HTTPUpload
from Products.ExtFile.ExtFile import ViewPermission
from Products.ExtFile.ExtFile import AccessPermission
from Products.ExtFile.ExtFile import ChangePermission
from Products.ExtFile.ExtFile import IDAVAware

from configuration import NO_PREVIEW
from configuration import GENERATE
from configuration import UPLOAD_NORESIZE
from configuration import UPLOAD_RESIZE
from configuration import REPOSITORY_UMASK

import logging

_SUBSYS = 'ExtImage'
_debug = 0
logger = logging.getLogger(_SUBSYS)

manage_addExtImageForm = HTMLFile('www/extImageAdd', globals())


def manage_addExtImage(self, id='', title='', descr='', file='', preview='',
                       content_type='', create_prev=NO_PREVIEW, maxx='', maxy='',
                       ratio=0, permission_check=0, redirect_default_view=0, REQUEST=None):
    """ Add an ExtImage to a folder. """
    if not id and getattr(file, 'filename', None) is not None:
        # generate id from filename and make sure, it has no 'bad' chars
        id = file.filename
        id = id[max(string.rfind(id,'/'),
                    string.rfind(id,'\\'),
                    string.rfind(id,':'))+1:]
        title = title or id
        id = normalize_id(id)
    tempExtImage = ExtImage(id, title, descr, permission_check, redirect_default_view)
    self._setObject(id, tempExtImage)
    if file != '':
        self._getOb(id).manage_file_upload(file, content_type, 0, create_prev, maxx, maxy, ratio)
    if preview != '' and (create_prev==UPLOAD_NORESIZE or create_prev==UPLOAD_RESIZE):
        self._getOb(id).manage_file_upload(preview, '', 1, create_prev, maxx, maxy, ratio)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=0)
    return id


class ExtImage(ExtFile):
    """ The ExtImage-Product works like the Zope Image-product, but stores the
        uploaded image externally in a repository-directory. It can create a
        preview of the image (requires PIL)."""

    if IDAVAware is not None:
        interface.implements(IExtImage, IWriteLock, IDAVAware)
    else:
        interface.implements(IExtImage, IWriteLock)

    security = ClassSecurityInfo()

    # what do people think they're adding?
    meta_type = 'ExtImage'

    # default,min,max-sizes for the preview image
    _image_size={'default':256,'min':1,'max':999}

    # store maxx and maxy
    prev_maxx = _image_size['default']
    prev_maxy = _image_size['default']

    ################################
    # Init method                  #
    ################################

    def __init__(self, id, title='', descr='', permission_check=0, redirect_default_view=0):
        """ Initialize a new instance of ExtImage """
        super(ExtImage, self).__init__(id, title, descr, permission_check, redirect_default_view)
        self.prev_filename = []
        self.prev_content_type = ''
        self.prev_ratio = 1
        self.has_preview = 0

    ################################
    # Public methods               #
    ################################

    def __str__(self):
        return self.tag()

    security.declareProtected(ViewPermission, 'tag')
    def tag(self, preview=0, icon=0, height=None, width=None, alt=None,
            scale=0, xscale=0, yscale=0, border='0', REQUEST=None,
            title=None, css_class=None, **args):
        """ Generate an HTML IMG tag for this image, with customization.
            Arguments to self.tag() can be any valid attributes of an IMG tag.
            'src' will always be an absolute pathname, to prevent redundant
            downloading of images. Defaults are applied intelligently for
            'height', 'width', and 'alt'. If specified, the 'scale', 'xscale',
            and 'yscale' keyword arguments will be used to automatically adjust
            the output height and width values of the image tag.
            Adopted and adapted from OFS/Image.py
        """
        if not self.is_webviewable():
            preview = 1
        if not self._access_permitted():
            preview = 1
        if preview and not self.has_preview:
            icon = 1
        if icon:
            url = self._static_url(icon=1)
            img_width, img_height = (32, 32)
        elif preview:
            url = self._static_url(preview=1)
            img_width, img_height = self._getImageSize(self.prev_filename)
        else:
            url = self._static_url()
            img_width, img_height = self._getImageSize(self.filename)
        height = height or img_height
        width = width or img_width

        # Auto-scaling support
        xdelta = xscale or scale
        ydelta = yscale or scale
        if xdelta and width != None:
            width = str(int(int(width) * xdelta))
        if ydelta and height != None:
            height = str(int(int(height) * ydelta))

        result = '<img src="%s"' % (url,)
        if alt is None:
            alt = getattr(self, 'alt', '')
        result = '%s alt="%s"' % (result, html_quote(alt))
        if title is None:
            title = getattr(self, 'title', '')
        result = '%s title="%s"' % (result, html_quote(title))
        if height:
            result = '%s height="%s"' % (result, height)
        if width:
            result = '%s width="%s"' % (result, width)
        # Omitting 'border' attribute (Collector #1557)
        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)
        for key in args.keys():
            value = args.get(key)
            if value:
                result = '%s %s="%s"' % (result, key, value)
        return '%s />' % result

    security.declareProtected(ViewPermission, 'preview')
    def preview(self):
        """ Return a preview of the image """
        raise Redirect(self._static_url(preview=1))

    security.declareProtected(ViewPermission, 'preview_tag')
    def preview_tag(self, height=None, width=None, alt=None,
                    scale=0, xscale=0, yscale=0,
                    title=None, css_class=None, **args):
        """ Generates an HTML IMG tag for the preview image """
        return self.tag(preview=1, height=height, width=width, alt=alt,
                        scale=scale, xscale=xscale, yscale=yscale,
                        title=title, css_class=css_class, **args)

    security.declareProtected(ViewPermission, 'preview_html')
    def preview_html(self):
        """ Same as preview_tag """
        return self.preview_tag()

    security.declareProtected(ViewPermission, 'preview_link')
    def preview_link(self, text=None, structure=False,
                     title=None, css_class=None, **args):
        """ Returns an HTML link tag for the preview image.
        """
        return self.link(preview=1, text=text, structure=structure,
                         title=title, css_class=css_class, **args)

    security.declareProtected(ViewPermission, 'thumbnail_tag')
    def thumbnail_tag(self, size=180):
        """ Returns the HTML image tag for a thumbnail view of this image.
            Used by the ZMI.
        """
        # Try hard to return something useful even in the face of breakage
        size = max(0, size)
        if self.has_preview:
            if self._get_fsname(self.prev_filename):
                width, height = self._getImageSize(self.prev_filename)
                if width > size or height > size:
                    return self.tag(preview=1, scale=float(size)/max(width, height))
                else:
                    return self.tag(preview=1)
            else:
                # tag() is too helpful here...
                return '<img src="%s?preview=1" alt="" title="" height="32" width="32" />' % \
                            (self.absolute_url(),)
        else:
            if self.is_webviewable():
                width, height = self._getImageSize(self.filename)
                if width > size or height > size:
                    return self.tag(scale=float(size)/max(width, height))
                else:
                    return self.tag()
            else:
                if self._get_fsname(self.filename):
                    return self.tag(icon=1)
                else:
                    # tag() is too helpful here...
                    return '<img src="%s" alt="" title="" height="32" width="32" />' % \
                                (self.absolute_url(),)

    security.declareProtected(ViewPermission, 'is_broken')
    def is_broken(self):
        """ Check if external file exists and return true (1) or false (0) """
        if self.has_preview and self.filename != self.prev_filename:
            if not self._get_fsname(self.prev_filename):
                return 1
        return super(ExtImage, self).is_broken()

    security.declareProtected(ViewPermission, 'is_webviewable')
    def is_webviewable(self):
        """ Return 1 for GIF, JPEG, and PNG images, otherwise return 0 """
        format = self.format()
        if format=='JPEG' or format=='GIF' or format=='PNG':
            return 1
        else:
            return 0

    security.declareProtected(ViewPermission, 'get_prev_size')
    def get_prev_size(self):
        """ Returns the size of the preview file """
        fn = self._get_fsname(self.prev_filename)
        if fn:
            return os.stat(fn)[6]
        return 0

    security.declareProtected(ViewPermission, 'prev_rawsize')
    def prev_rawsize(self):
        """ Same as get_prev_size """
        return self.get_prev_size()

    security.declareProtected(ViewPermission, 'prev_size')
    def prev_size(self):
        """ Returns a formatted stringified version of the preview size """
        return self._bytetostring(self.get_prev_size())

    security.declareProtected(ViewPermission, 'width')
    def width(self):
        """ Pixel width of the image """
        return self._getImageSize(self.filename)[0]

    security.declareProtected(ViewPermission, 'height')
    def height(self):
        """ Pixel height of the image """
        return self._getImageSize(self.filename)[1]

    security.declareProtected(ViewPermission, 'prev_width')
    def prev_width(self):
        """ Pixel width of the preview """
        return self._getImageSize(self.prev_filename)[0]

    security.declareProtected(ViewPermission, 'prev_height')
    def prev_height(self):
        """ Pixel height of the preview """
        return self._getImageSize(self.prev_filename)[1]

    security.declareProtected(ViewPermission, 'format')
    def format(self):
        """ Get the PIL file format of the image """
        filename = self._get_fsname(self.filename)
        try:
            from PIL import Image
            im = Image.open(filename)
            return im.format
        except:
            return 'unknown'

    security.declareProtected(AccessPermission, 'get_prev_filename')
    def get_prev_filename(self):
        """ Returns the preview file name for display """
        return self._fsname(self.prev_filename)

    ################################
    # Protected management methods #
    ################################

    # Management Interface
    security.declareProtected(AccessPermission, 'manage_main')
    manage_main = HTMLFile('www/extImageEdit', globals())

    security.declareProtected(ChangePermission, 'manage_del_prev')
    def manage_del_prev(self, REQUEST=None):
        """ Delete the Preview Image """
        if self.has_preview and self.filename != self.prev_filename:
            self._delete(self.prev_filename)
        self.prev_content_type = ''
        self.has_preview = 0

        self.ZCacheable_invalidate()

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Preview deleted.')

    security.declareProtected(ChangePermission, 'manage_create_prev')
    def manage_create_prev(self, maxx=0, maxy=0, ratio=0, REQUEST=None):
        """ Create a preview Image """
        maxx, maxy = self._formatDimensions(maxx, maxy)
        if maxx!=0 and maxy!=0:
            self._register()    # Register with TM
            try:
                new_fn = self._get_ufn(self.prev_filename, content_type='image/jpeg')
                self._createPreview(self.filename, new_fn, maxx, maxy, ratio)
            finally:
                self._dir__unlock()
        if REQUEST is None:
            return self.has_preview
        else:
            if self.has_preview:
                return self.manage_main(self, REQUEST, manage_tabs_message='Preview created.')
            elif maxx=='0' and maxy=='0':
                return MessageDialog(
                    title = 'Attention',
                    message = "You must enter a value > 0",
                    action = './manage_main',)
            else:
                return MessageDialog(
                    title = 'Warning',
                    message = "An error occurred while generating the preview.",
                    action = './manage_main',)

    # File upload Interface
    security.declareProtected(AccessPermission, 'manage_uploadForm')
    manage_uploadForm = HTMLFile('www/extImageUpload', globals())

    security.declareProtected(ChangePermission, 'manage_upload')
    def manage_upload(self, file='', content_type='', is_preview=0,
                      create_prev=NO_PREVIEW, maxx='', maxy='', ratio=0,
                      REQUEST=None):
        """ Upload image from file handle, Pdata, or string buffer """
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        if isinstance(file, str):
            temp_file = TemporaryFile()
            temp_file.write(file)
            temp_file.seek(0)
        else:
            temp_file = file
        return self.manage_file_upload(temp_file, content_type, is_preview,
                                       create_prev, maxx, maxy, ratio, REQUEST)

    security.declareProtected(ChangePermission, 'manage_file_upload')
    def manage_file_upload(self, file='', content_type='', is_preview=0,
                           create_prev=NO_PREVIEW, maxx='', maxy='', ratio=0,
                           REQUEST=None):
        """ Upload image from file handle, Pdata, or local directory """
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        if is_preview:
            if isinstance(file, str):
                file = open(file, 'rb')
            elif isinstance(file, Pdata):
                file = pdata(file)
            maxx, maxy = self._formatDimensions(maxx, maxy)
            if create_prev==UPLOAD_RESIZE and maxx!=0 and maxy!=0:
                self._register()    # Register with TM
                try:
                    new_fn = self._get_ufn(self.prev_filename, content_type='image/jpeg')
                    self._update_data(file, self._temp_fsname(new_fn))
                finally:
                    self._dir__unlock()
                self._createPreview(new_fn, new_fn, maxx, maxy, ratio)
            else:
                if content_type:
                    file = HTTPUpload(file, content_type)
                content_type = self._get_content_type(file, file.read(100),
                                                      self._get_zodb_id(), self.prev_content_type)
                file.seek(0)
                self._register()    # Register with TM
                try:
                    backup = self.prev_filename and self._changed(self.prev_content_type, content_type)
                    new_fn = self._get_ufn(self.prev_filename, content_type=content_type, backup=backup)
                    self._update_data(file, self._temp_fsname(new_fn))
                finally:
                    self._dir__unlock()
                self.prev_filename = new_fn
                self.prev_content_type = content_type
                self._initPreview()
        else:
            super(ExtImage, self).manage_file_upload(file, content_type)
            if create_prev==GENERATE:
                maxx, maxy = self._formatDimensions(maxx, maxy)
                if maxx!=0 and maxy!=0:
                    self._register()    # Register with TM
                    try:
                        new_fn = self._get_ufn(self.prev_filename, content_type='image/jpeg')
                        self._createPreview(self.filename, new_fn, maxx, maxy, ratio)
                    finally:
                        self._dir__unlock()
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Upload complete.')

    security.declareProtected(ChangePermission, 'manage_http_upload')
    def manage_http_upload(self, url, is_preview=0, REQUEST=None):
        """ Upload image from http-server """
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        if is_preview:
            url = urllib.quote(url,'/:')
            file = urllib.urlopen(url)
            file = HTTPUpload(file)
            content_type = self._get_content_type(file, file.read(100),
                                                  self._get_zodb_id(), self.prev_content_type)
            file.seek(0)
            self._register()    # Register with TM
            try:
                backup = self.prev_filename and self._changed(self.prev_content_type, content_type)
                new_fn = self._get_ufn(self.prev_filename, content_type=content_type, backup=backup)
                self._update_data(file, self._temp_fsname(new_fn))
            finally:
                self._dir__unlock()
            self.prev_filename = new_fn
            self.prev_content_type = content_type
            self._initPreview()
        else:
            super(ExtImage, self).manage_http_upload(url)
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Upload complete.')

    security.declareProtected(ChangePermission, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP PUT requests """
        RESPONSE = super(ExtImage, self).PUT(REQUEST, RESPONSE)
        if self.has_preview:
            maxx, maxy = self._formatDimensions(self.prev_maxx, self.prev_maxy)
            self._register()    # Register with TM
            try:
                new_fn = self._get_ufn(self.prev_filename, content_type='image/jpeg')
                self._createPreview(self.filename, new_fn, maxx, maxy, self.prev_ratio)
            finally:
                self._dir__unlock()
        return RESPONSE

    ################################
    # Private methods              #
    ################################

    def _getImageSize(self, filename):
        """ Return width, height tuple using PIL """
        filename = self._get_fsname(filename)
        try:
            from PIL import Image
            im = Image.open(filename)
            return im.size[0], im.size[1]
        except:
            return 0, 0

    def _createPreview(self, from_filename, to_filename, maxx, maxy, ratio):
        """ Generate a preview using PIL """
        try:
            from PIL import Image
        except ImportError:
            pass
        else:
            imfile = self._get_fsname(from_filename)
            if imfile:
                im = Image.open(imfile)
                if im.mode!='RGB':
                    im = im.convert('RGB')
                filter = Image.BICUBIC
                if hasattr(Image, 'ANTIALIAS'): # PIL 1.1.3
                    filter = Image.ANTIALIAS
                if ratio:               # keep aspect-ratio
                    im.thumbnail((maxx,maxy), filter)
                else:                   # distort to fixed size
                    im = im.resize((maxx,maxy), filter)
                umask = os.umask(REPOSITORY_UMASK)
                outfile = self._temp_fsname(to_filename)
                try:
                    im.save(outfile, 'JPEG', quality=85)
                except:
                    os.umask(umask)
                    if isfile(outfile):
                        try:
                            os.remove(outfile)
                        except OSError:
                            logger.error('_createPreview', exc_info=True)
                    raise
                else:
                    os.umask(umask)
                self.prev_content_type = 'image/jpeg'
                self.prev_filename = to_filename
                self.prev_maxx = maxx
                self.prev_maxy = maxy
                self.prev_ratio = ratio
        self._initPreview()

    def _initPreview(self):
        """ Verify the preview """
        self.ZCacheable_invalidate()

        prev_width, prev_height = self._getImageSize(self.prev_filename)
        if prev_width<=0 or prev_height<=0:
            self.has_preview = 0
        else:
            self.has_preview = 1

    def _formatDimensions(self, maxx, maxy):
        """ Make sure, the dimensions are valid int's """
        if isinstance(maxx, str):
            try: maxx = int(maxx)
            except ValueError: maxx = self._image_size['default']
        if isinstance(maxy, str):
            try: maxy = int(maxy)
            except ValueError: maxy = self._image_size['default']
        if maxx!=0 and maxy!=0:
            if maxx<self._image_size['min']: maxx = self._image_size['min']
            elif maxx>self._image_size['max']: maxx = self._image_size['max']
            if maxy<self._image_size['min']: maxy = self._image_size['min']
            elif maxy>self._image_size['max']: maxy = self._image_size['max']
        return maxx, maxy

    def _get_content_type(self, file, body, id, content_type=None):
        """ Determine the mime-type """
        ct, w, h = getImageInfo(body)
        if ct:
            content_type = ct
        else:
            content_type = super(ExtImage, self)._get_content_type(
                                                    file, body, id, content_type)
        return content_type

    def _afterUpdate(self):
        """ Called whenever the image data has been updated.
            Fires an ExtImageUpdatedEvent.
        """
        self.ZCacheable_invalidate()
        event.notify(ExtImageUpdatedEvent(self))

    ################################
    # Transaction manager methods  #
    ################################

    def _finish(self):
        """ Commits the temporary file """
        if self.prev_filename and self.filename != self.prev_filename:
            tmp_fn = self._temp_fsname(self.prev_filename)
            if _debug: logger.info('finishing %s' % tmp_fn)
            if isfile(tmp_fn):
                if _debug: logger.info('isfile %s' % tmp_fn)
                fn = self._fsname(self.prev_filename)
                if isfile(fn):
                    try:
                        os.remove(fn)
                    except OSError:
                        logger.error('_finish', exc_info=True)
                try:
                    os.rename(tmp_fn, fn)
                except OSError:
                    logger.error('_finish', exc_info=True)
        super(ExtImage, self)._finish()

    def _abort(self):
        """ Deletes the temporary file """
        if self.prev_filename and self.filename != self.prev_filename:
            tmp_fn = self._temp_fsname(self.prev_filename)
            if _debug: logger.info('aborting %s' % tmp_fn)
            if isfile(tmp_fn):
                if _debug: logger.info('isfile %s' % tmp_fn)
                try:
                    os.remove(tmp_fn)
                except OSError:
                    logger.error('_abort', exc_info=True)
        super(ExtImage, self)._abort()

InitializeClass(ExtImage)


# Event handlers
def afterClone(self, event):
    """ When a copy of the object is created (zope copy-paste-operation),
        this function is called by CopySupport.py. A copy of the external
        file is created and self.filename is changed.

        Subscriber for (IExtImage, IObjectClonedEvent)
    """
    # We have been copied, also copy the preview file
    if self.has_preview and self.filename != self.prev_filename:
        fn = self._get_fsname(self.prev_filename)
        if fn:
            self._register()    # Register with TM
            try:
                new_fn = self._get_new_ufn(content_type=self.prev_content_type)
                self._update_data(fn, self._temp_fsname(new_fn))
                self.prev_filename = new_fn
            finally:
                self._dir__unlock()
    elif not self.has_preview:
        self.prev_filename = []


def afterAdd(self, event):
    """ This method is called, whenever _setObject in ObjectManager gets
        called. This is the case after a normal add and if the object is a
        result of cut-paste- or rename-operation. In the first case, the
        external files doesn't exist yet, otherwise it was renamed to .undo
        by beforeDelete before and must be restored by _undo().

        Subscriber for (IExtImage, IObjectMovedEvent)
    """
    from zope.app.container.interfaces import IObjectAddedEvent
    from zope.app.container.interfaces import IObjectRemovedEvent

    # If this is a Removed event we are done
    if IObjectRemovedEvent.providedBy(event):
        return

    # The preview file has been renamed to .undo by beforeDelete
    if self.has_preview and self.filename != self.prev_filename:
        self._undo(self.prev_filename)

    # If this is an Added event we are done
    if IObjectAddedEvent.providedBy(event):
        return

    # We have been moved, also move the preview file
    if self.has_preview and self.filename != self.prev_filename:
        fn = self._get_fsname(self.prev_filename)
        if fn:
            self._register()    # Register with TM
            try:
                new_fn = self._get_new_ufn(content_type=self.prev_content_type)
                self._update_data(fn, self._temp_fsname(new_fn))
                self._delete(self.prev_filename)
                self.prev_filename = new_fn
            finally:
                self._dir__unlock()
    elif not self.has_preview:
        self.prev_filename = []


def beforeDelete(self, event):
    """ This method is called, when the object is deleted. To support
        undo-functionality and because this happens too, when the object
        is moved (cut-paste) or renamed, the external file is not deleted.
        It is just renamed to filename.undo and remains in the
        repository, until it is deleted manually.

        Subscriber for (IExtImage, IObjectWillBeMovedEvent)
    """
    from OFS.interfaces import IObjectWillBeAddedEvent

    # If this is an Add event we are done
    if IObjectWillBeAddedEvent.providedBy(event):
        return

    # Delete the preview file, i.e. rename it to .undo
    if self.has_preview and self.filename != self.prev_filename:
        self._delete(self.prev_filename)
