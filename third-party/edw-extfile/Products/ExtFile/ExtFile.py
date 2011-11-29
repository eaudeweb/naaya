""" ExtFile product module """
# -*- coding: latin-1 -*-
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

__doc__ = """ExtFile product module.
    The ExtFile-Product works like the Zope File-product, but stores
    the uploaded file externally in a repository-direcory."""

__version__='2.0.2'

from Products.ZCatalog.CatalogPathAwareness import CatalogAware
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from OFS.Cache import Cacheable
from OFS.Image import Pdata
from Globals import HTMLFile, MessageDialog, InitializeClass, package_home
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl import Permissions
from Acquisition import aq_acquire, aq_base
from webdav.Lockable import ResourceLockedError
from webdav.common import rfc1123_date
from DateTime import DateTime
import urllib, os, string, sha, base64
import mimetypes, re, time, threading
from os.path import join, isfile
from tempfile import TemporaryFile
from Products.ExtFile import TM
from zExceptions import Redirect
from ZPublisher.Iterators import IStreamIterator
from DocumentTemplate.html_quote import html_quote

try:
    from webdav.interfaces import IWriteLock
except ImportError: #< zope2.12
    from webdav.WriteLockInterface import WriteLockInterface as IWriteLock

from zope import interface
from interfaces import IExtFile
from zope import event
from interfaces import ExtFileUpdatedEvent

import logging

_SUBSYS = 'ExtFile'
_debug = 0
logger = logging.getLogger(_SUBSYS)

try:
    from zope.contenttype import guess_content_type
except ImportError:
    from zope.app.content_types import guess_content_type

try:
    from Products.GenericSetup.interfaces import IDAVAware
except ImportError:
    IDAVAware = None

here = package_home(globals())

ViewPermission = Permissions.view
AccessPermission = Permissions.view_management_screens
ChangePermission = 'Change ExtFile/ExtImage'
DownloadPermission = 'Download ExtFile/ExtImage'

from configuration import *

manage_addExtFileForm = HTMLFile('www/extFileAdd', globals())


def manage_addExtFile(self, id='', title='', descr='', file='',
                      content_type='', permission_check=0, redirect_default_view=0, REQUEST=None):
    """ Add an ExtFile to a folder. """
    if not id and getattr(file, 'filename', None) is not None:
        # generate id from filename and make sure, it has no 'bad' chars
        id = file.filename
        id = id[max(string.rfind(id,'/'),
                    string.rfind(id,'\\'),
                    string.rfind(id,':'))+1:]
        title = title or id
        id = normalize_id(id)
    tempExtFile = ExtFile(id, title, descr, permission_check, redirect_default_view)
    self._setObject(id, tempExtFile)
    if file != '':
        self._getOb(id).manage_file_upload(file, content_type)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=0)
    return id


class ExtFile(CatalogAware, SimpleItem, PropertyManager, Cacheable):
    """ The ExtFile-Product works like the Zope File-product, but stores
        the uploaded file externally in a repository-directory. """

    if IDAVAware is not None:
        interface.implements(IExtFile, IWriteLock, IDAVAware)
    else:
        interface.implements(IExtFile, IWriteLock)

    # what properties have we?
    _properties = (
        {'id':'title',                          'type':'string',    'mode': 'w'},
        {'id':'descr',                          'type':'text',      'mode': 'w'},
        {'id':'content_type',                   'type':'string',    'mode': 'w'},
        {'id':'use_download_permission_check',  'type':'boolean',   'mode': 'w'},
        {'id':'redirect_default_view',          'type':'boolean',   'mode': 'w'},
    )
    use_download_permission_check = 0
    redirect_default_view = 0

    # what management options are there?
    manage_options = ((
        {'label':'Edit',            'action': 'manage_main'             },
        {'label':'View',            'action': ''                        },
        {'label':'Upload',          'action': 'manage_uploadForm'       },) +
        PropertyManager.manage_options +
        SimpleItem.manage_options[1:] +
        Cacheable.manage_options
    )

    security = ClassSecurityInfo()

    # what do people think they're adding?
    meta_type = 'ExtFile'

    # make sure the download permission is available
    security.setPermissionDefault(DownloadPermission, ('Manager',))

    # MIME-Type Dictionary. To add a MIME-Type, add a file in the directory
    # icons/_category_/_subcategory-icon-file_
    # example: Icon tifficon.gif for the MIME-Type image/tiff goes to
    # icons/image/tifficon.gif and the dictionary must be updated like this:
    # 'image':{'tiff':'tifficon.gif','default':'default.gif'}, ...
    _types={'image':
                {'default':'default.gif'},
            'text':
                {'html':'html.gif', 'xml':'xml.gif', 'default':'default.gif',
                 'python':'py.gif'},
            'application':
                {'pdf':'pdf.gif', 'zip':'zip.gif', 'tar':'zip.gif',
                 'msword':'doc.gif', 'excel':'xls.gif', 'powerpoint':'ppt.gif',
                 'default':'default.gif'},
            'video':
                {'default':'default.gif'},
            'audio':
                {'default':'default.gif'},
            'default':'default.gif'
        }

    ################################
    # Init method                  #
    ################################

    def __init__(self, id, title='', descr='', permission_check=0, redirect_default_view=0):
        """ Initialize a new instance of ExtFile """
        self.id = id
        self.title = title
        self.descr = descr
        self.use_download_permission_check = permission_check
        self.redirect_default_view = redirect_default_view
        self.__version__ = __version__
        self.filename = []
        self.content_type = ''

    ################################
    # Public methods               #
    ################################

    @property
    def data(self):
        if self.is_broken():
            return ''
        return self.index_html()

    def __str__(self):
        return self.data

    def __len__(self):
        return 1

    def _if_modified_since_request_handler(self, REQUEST):
        """ HTTP If-Modified-Since header handling: return True if
            we can handle this request by returning a 304 response.
        """
        header = REQUEST.get_header('If-Modified-Since', None)
        if header is not None:
            header = string.split(header, ';')[0]
            try:    mod_since = long(DateTime(header).timeTime())
            except: mod_since = None
            if mod_since is not None:
                if self._p_mtime:
                    last_mod = long(self._p_mtime)
                else:
                    last_mod = long(0)
                if last_mod > 0 and last_mod <= mod_since:
                    # Set headers for Apache caching
                    last_mod = rfc1123_date(self._p_mtime)
                    REQUEST.RESPONSE.setHeader('Last-Modified', last_mod)
                    REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
                    # RFC violation. See http://www.zope.org/Collectors/Zope/544
                    #REQUEST.RESPONSE.setHeader('Content-Length', self.get_size())
                    REQUEST.RESPONSE.setStatus(304)
                    return 1

    def _redirect_default_view_request_handler(self, icon, preview, REQUEST):
        """ redirect_default_view property handling: return True if
            we can handle this request by returning a 302 response.
            Patch provided by Oliver Bleutgen.
        """
        if self.redirect_default_view:
            if self.static_mode() and not icon:
                static_url = self._static_url(preview=preview)
                if static_url != self.absolute_url():
                    REQUEST.RESPONSE.redirect(static_url)
                    return 1

    security.declareProtected(ViewPermission, 'index_html')
    def index_html (self, icon=0, preview=0, width=None, height=None,
                    REQUEST=None, RESPONSE=None):
        """ Return the file with it's corresponding MIME-type """

        if REQUEST is not None:
            if self._if_modified_since_request_handler(REQUEST):
                self.ZCacheable_set(None)
                return ''

            if self._redirect_default_view_request_handler(icon, preview, REQUEST):
                return ''

        filename, content_type, icon, preview = self._get_file_to_serve(icon, preview)
        filename = self._get_fsname(filename)

        if _debug > 1: logger.info('serving %s, %s, %s, %s' %(filename, content_type, icon, preview))

        if filename:
            size = os.stat(filename)[6]
        else:
            filename = self._get_icon_file(broken=True)
            size = os.stat(filename)[6]
            content_type = 'image/gif'
            icon = 1

        if icon==0 and width is not None and height is not None:
            data = TemporaryFile() # hold resized image
            try:
                from PIL import Image
                im = Image.open(filename)
                if im.mode!='RGB':
                    im = im.convert('RGB')
                filter = Image.BICUBIC
                if hasattr(Image, 'ANTIALIAS'): # PIL 1.1.3
                    filter = Image.ANTIALIAS
                im = im.resize((int(width),int(height)), filter)
                im.save(data, 'JPEG', quality=85)
            except:
                data = open(filename, 'rb')
            else:
                data.seek(0,2)
                size = data.tell()
                data.seek(0)
                content_type = 'image/jpeg'
        else:
            data = open(filename, 'rb')

        if REQUEST is not None:
            last_mod = rfc1123_date(self._p_mtime)
            REQUEST.RESPONSE.setHeader('Last-Modified', last_mod)
            REQUEST.RESPONSE.setHeader('Content-Type', content_type)
            REQUEST.RESPONSE.setHeader('Content-Length', size)
            self.ZCacheable_set(None)
            return stream_iterator(data)

        try:
            return data.read()
        finally:
            data.close()

    security.declareProtected(ViewPermission, 'view_image_or_file')
    def view_image_or_file(self):
        """ The default view of the contents of the File or Image. """
        raise Redirect(self.absolute_url())

    security.declareProtected(ViewPermission, 'link')
    def link(self, text=None, structure=False, title=None, css_class=None,
             icon=0, preview=0, **args):
        """ Returns an HTML link tag for the file or image.
            The 'text' argument is subject to HTML-quoting. To pass a
            structure (e.g. an <img /> tag), set the 'structure' keyword
            argument to True.
        """
        href = self._static_url(icon=icon, preview=preview)
        if text is None:
            text = html_quote(self.title_or_id())
        elif not structure:
            text = html_quote(text)
        if title is None:
            title = getattr(self, 'title', '')
        title = html_quote(title)
        return self._link(href, text, title, css_class, **args)

    security.declareProtected(ViewPermission, 'icon_gif')
    def icon_gif(self):
        """ Return an icon for the file's MIME-Type """
        raise Redirect(self._static_url(icon=1))

    security.declareProtected(ViewPermission, 'icon_tag')
    def icon_tag(self):
        """ Generate the HTML IMG tag for the icon """
        return '<img src="%s" border="0" />' % self._static_url(icon=1)

    security.declareProtected(ViewPermission, 'icon_html')
    def icon_html(self):
        """ Same as icon_tag """
        return self.icon_tag()

    security.declareProtected(ViewPermission, 'is_broken')
    def is_broken(self):
        """ Check if external file exists and return true (1) or false (0) """
        return not self._get_fsname(self.filename)

    security.declareProtected(ViewPermission, 'get_size')
    def get_size(self):
        """ Returns the size of the file or image """
        fn = self._get_fsname(self.filename)
        if fn:
            return os.stat(fn)[6]
        return 0

    security.declareProtected(ViewPermission, 'rawsize')
    def rawsize(self):
        """ Same as get_size """
        return self.get_size()

    security.declareProtected(ViewPermission, 'getSize')
    def getSize(self):
        """ Same as get_size """
        return self.get_size()

    security.declareProtected(ViewPermission, 'size')
    def size(self):
        """ Returns a formatted stringified version of the file size """
        return self._bytetostring(self.get_size())

    security.declareProtected(ViewPermission, 'getContentType')
    def getContentType(self):
        """ Returns the content type (MIME type) of a file or image. """
        return self.content_type

    security.declareProtected(ViewPermission, 'getIconPath')
    def getIconPath(self, broken=False):
        """ Depending on the MIME Type of the file/image an icon
            can be displayed. This function determines which
            image in the Products/ExtFile/www/icons/...  directory
            should be used as icon for this file/image.
        """
        if broken:
            return join('www', 'icons', 'broken.gif')
        try:
            cat, sub = string.split(self.content_type, '/')
        except ValueError:
            if getattr(self, 'has_preview', None) is not None:
                cat, sub = 'image', ''
            else:
                cat, sub = '', ''
        if self._types.has_key(cat):
            file = self._types[cat]['default']
            for item in self._types[cat].keys():
                if string.find(sub, item) >= 0:
                    file = self._types[cat][item]
                    break
            return join('www', 'icons', cat, file)
        return join('www', 'icons', self._types['default'])

    security.declareProtected(ViewPermission, 'static_url')
    def static_url(self, icon=0, preview=0):
        """ In static mode, returns the static url of the file,
            absolute_url otherwise.
        """
        return self._static_url(icon, preview)

    security.declareProtected(ViewPermission, 'static_mode')
    def static_mode(self):
        """ Returns true if we are serving static urls """
        return os.environ.get('EXTFILE_STATIC_PATH') is not None

    security.declareProtected(AccessPermission, 'get_filename')
    def get_filename(self):
        """ Returns the filename as filesystem path.
            Used by the ZMI to display the filename.
        """
        return self._fsname(self.filename)

    security.declareProtected(ViewPermission, 'PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        """ Allow file objects to be searched.
        """
        if self.content_type.startswith('text/'):
            return str(self)
        return ''

    ################################
    # Protected management methods #
    ################################

    # Management Interface
    security.declareProtected(AccessPermission, 'manage_main')
    manage_main = HTMLFile('www/extFileEdit', globals())

    security.declareProtected(ChangePermission, 'manage_editExtFile')
    def manage_editExtFile(self, title='', descr='', REQUEST=None):
        """ Manage the edited values """
        if self.title!=title: self.title = title
        if self.descr!=descr: self.descr = descr
        # update ZCatalog
        self.reindex_object()

        self.ZCacheable_invalidate()

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Saved changes.')

    # File upload Interface
    security.declareProtected(AccessPermission, 'manage_uploadForm')
    manage_uploadForm = HTMLFile('www/extFileUpload', globals())

    security.declareProtected(ChangePermission, 'manage_upload')
    def manage_upload(self, file='', content_type='', REQUEST=None):
        """ Upload file from file handle, Pdata, or string buffer """
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        if isinstance(file, str):
            temp_file = TemporaryFile()
            temp_file.write(file)
            temp_file.seek(0)
        else:
            temp_file = file
        return self.manage_file_upload(temp_file, content_type, REQUEST)

    security.declareProtected(ChangePermission, 'manage_file_upload')
    def manage_file_upload(self, file='', content_type='', REQUEST=None):
        """ Upload file from file handle, Pdata, or local directory"""
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        if isinstance(file, str):
            file = open(file, 'rb')
        elif isinstance(file, Pdata):
            file = pdata(file)
        if content_type:
            file = HTTPUpload(file, content_type)
        content_type = self._get_content_type(file, file.read(100),
                                              self._get_zodb_id(), self.content_type)
        file.seek(0)
        self._register()    # Register with TM
        try:
            backup = self.filename and self._changed(self.content_type, content_type)
            new_fn = self._get_ufn(self.filename, content_type=content_type, backup=backup)
            self._update_data(file, self._temp_fsname(new_fn))
        finally:
            self._dir__unlock()
        self.filename = new_fn
        self.content_type = content_type
        self._afterUpdate()
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Upload complete.')

    security.declareProtected(ChangePermission, 'manage_http_upload')
    def manage_http_upload(self, url, REQUEST=None):
        """ Upload file from http-server """
        if self.wl_isLocked():
            raise ResourceLockedError("File is locked via WebDAV")

        url = urllib.quote(url,'/:')
        file = urllib.urlopen(url)
        file = HTTPUpload(file)
        content_type = self._get_content_type(file, file.read(100),
                                              self._get_zodb_id(), self.content_type)
        file.seek(0)
        self._register()    # Register with TM
        try:
            backup = self.filename and self._changed(self.content_type, content_type)
            new_fn = self._get_ufn(self.filename, content_type=content_type, backup=backup)
            self._update_data(file, self._temp_fsname(new_fn))
        finally:
            self._dir__unlock()
        self.filename = new_fn
        self.content_type = content_type
        self._afterUpdate()
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Upload complete.')

    security.declareProtected(ChangePermission, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP PUT requests """
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        file = REQUEST['BODYFILE']
        content_type = REQUEST.get_header('content-type', None)
        if content_type:
            file = HTTPUpload(file, content_type)
        content_type = self._get_content_type(file, file.read(100),
                                              self._get_zodb_id(), self.content_type)
        file.seek(0)
        self._register()    # Register with TM
        try:
            backup = self.filename and self._changed(self.content_type, content_type)
            new_fn = self._get_ufn(self.filename, content_type=content_type, backup=backup)
            self._update_data(file, self._temp_fsname(new_fn))
        finally:
            self._dir__unlock()
        self.filename = new_fn
        self.content_type = content_type
        self._afterUpdate()
        RESPONSE.setStatus(204)
        return RESPONSE

    security.declareProtected('FTP access', 'manage_FTPstat')
    security.declareProtected('FTP access', 'manage_FTPlist')
    security.declareProtected('FTP access', 'manage_FTPget')
    def manage_FTPget(self):
        """ Return body for FTP """
        return self.index_html(REQUEST=self.REQUEST)

    ################################
    # Private methods              #
    ################################

    def _access_permitted(self, REQUEST=None):
        """ Check if the user is allowed to download the file """
        if REQUEST is None and getattr(self, 'REQUEST', None) is not None:
            REQUEST = self.REQUEST
        if getattr(self, 'use_download_permission_check', 0) and \
           (REQUEST is None or
            not getSecurityManager().getUser().has_permission(
                                        DownloadPermission, self)
           ):
            return 0
        else:
            return 1

    def _get_content_type(self, file, body, id, content_type=None):
        """ Determine the mime-type """
        headers = getattr(file, 'headers', None)
        if headers and headers.has_key('content-type'):
            content_type = headers['content-type']
        else:
            filename = getattr(file, 'filename', None) or id
            content_type, enc = guess_content_type(filename, body, content_type)
        cutoff = content_type.find(';')
        if cutoff >= 0:
            return content_type[:cutoff]
        return content_type

    def _update_data(self, infile, outfile):
        """ Store infile to outfile """
        if isinstance(infile, list):
            infile = self._fsname(infile)
        if isinstance(outfile, list):
            outfile = self._fsname(outfile)
        try:
            self._copy(infile, outfile)
        except:
            if isfile(outfile): # This is always a .tmp file
                try:
                    os.remove(outfile)
                except OSError:
                    logger.error('_update_data', exc_info=True)
            raise
        else:
            self.http__refreshEtag()

    def _copy(self, infile, outfile):
        """ Read binary data from infile and write it to outfile
            infile and outfile may be strings, in which case a file with that
            name is opened, or filehandles, in which case they are accessed
            directly.
        """
        if isinstance(infile, str):
            instream = open(infile, 'rb')
            close_in = 1
        else:
            instream = infile
            close_in = 0
        if isinstance(outfile, str):
            umask = os.umask(REPOSITORY_UMASK)
            try:
                outstream = open(outfile, 'wb')
                self._dir__unlock()   # unlock early
            finally:
                os.umask(umask)
            close_out = 1
        else:
            outstream = outfile
            close_out = 0
        blocksize = 2<<16
        block = instream.read(blocksize)
        outstream.write(block)
        while len(block)==blocksize:
            block = instream.read(blocksize)
            outstream.write(block)
        try: instream.seek(0)
        except: pass
        if close_in: instream.close()
        if close_out: outstream.close()

    def _delete(self, filename):
        """ Rename the file to .undo """
        tmp_fn = self._temp_fsname(filename)
        old_fn = self._fsname(filename)
        if isfile(tmp_fn):
            try:
                os.rename(tmp_fn, old_fn+'.undo')
            except OSError:
                logger.error('_delete', exc_info=True)
            else:
                if isfile(old_fn):
                    try:
                        os.remove(old_fn)
                    except OSError:
                        logger.error('_delete', exc_info=True)
        elif isfile(old_fn):
            try:
                os.rename(old_fn, old_fn+'.undo')
            except OSError:
                logger.error('_delete', exc_info=True)

    def _undo(self, filename):
        """ Restore filename after delete or copy-paste """
        fn = self._fsname(filename)
        if not isfile(fn) and isfile(fn+'.undo'):
            self._register()    # Register with TM
            try:
                os.rename(fn+'.undo', self._temp_fsname(filename))
            except OSError:
                logger.error('_undo', exc_info=True)

    def _fsname(self, filename):
        """ Generates the full filesystem name, incuding directories from
            REPOSITORY_PATH and filename
        """
        path = [INSTANCE_HOME]
        path.extend(REPOSITORY_PATH)
        if isinstance(filename, list):
            path.extend(filename)
        elif filename != '':
            path.append(filename)
        return join(*path)

    def _temp_fsname(self, filename):
        """ Generates the full filesystem name of the temporary file """
        return '%s.tmp' % self._fsname(filename)

    def _get_fsname(self, filename):
        """ Returns the full filesystem name, preferring tmp over main.
            Also attempts to undo. Returns None if the file is broken.
        """
        tmp_fn = self._temp_fsname(filename)
        if isfile(tmp_fn):
            return tmp_fn
        fn = self._fsname(filename)
        if isfile(fn):
            return fn
        self._undo(filename)
        if isfile(tmp_fn):
            return tmp_fn

    def _get_ufn(self, filename, path=None, content_type=None, lock=1, backup=0):
        """ If no unique filename has been generated, generate one.
            Otherwise, return the existing one.
        """
        if UNDO_POLICY==ALWAYS_BACKUP or backup or filename==[]:
            new_fn = self._get_new_ufn(path=path, content_type=content_type, lock=lock)
        else:
            new_fn = filename[:]
        if filename:
            if UNDO_POLICY==ALWAYS_BACKUP or backup:
                self._delete(filename)
            else:
                self._undo(filename)
        return new_fn

    def _get_new_ufn(self, path=None, content_type=None, lock=1):
        """ Create a new unique filename """
        id = self._get_zodb_id()

        # hack so the files are not named copy_of_foo
        if COPY_OF_PROTECTION:
            id = copy_of_protect(id)

        # get name and extension components from id
        pos = string.rfind(id, '.')
        if (pos+1):
            id_name = id[:pos]
            id_ext = id[pos:]
        else:
            id_name = id
            id_ext = ''

        if not content_type:
            content_type = self.content_type

        if REPOSITORY_EXTENSIONS in (MIMETYPE_APPEND, MIMETYPE_REPLACE):
            mime_ext = guess_extension(content_type)
            if mime_ext is not None:
                # don't change extensions of unknown binaries and text files
                if not (content_type in config.unknown_types and id_ext):
                    if REPOSITORY_EXTENSIONS == MIMETYPE_APPEND:
                        # don't append the same extension twice
                        if id_ext != mime_ext:
                            id_name = id_name + id_ext
                    id_ext = mime_ext

        # generate directory structure
        if path is not None:
            rel_url_list = path
        else:
            rel_url_list = self._get_zodb_path()

        dirs = []
        if REPOSITORY == SYNC_ZODB:
            dirs = rel_url_list
        elif REPOSITORY in (SLICED, SLICED_REVERSE, SLICED_HASH):
            if REPOSITORY == SLICED_HASH:
                # increase distribution by including the path in the hash
                hashed = ''.join(list(rel_url_list)+[id_name])
                temp = base64.encodestring(sha.new(hashed).digest())[:-1]
                temp = temp.replace('/', '_')
                temp = temp.replace('+', '_')
            elif REPOSITORY == SLICED_REVERSE:
                temp = list(id_name)
                temp.reverse()
                temp = ''.join(temp)
            else:
                temp = id_name
            for i in range(SLICE_DEPTH):
                if len(temp)<SLICE_WIDTH*(SLICE_DEPTH-i):
                    dirs.append(SLICE_WIDTH*'_')
                else:
                    dirs.append(temp[:SLICE_WIDTH])
                    temp=temp[SLICE_WIDTH:]
        elif REPOSITORY == CUSTOM:
            method = aq_acquire(self, CUSTOM_METHOD)
            dirs = method(rel_url_list, id)

        if NORMALIZE_CASE == NORMALIZE:
            dirs = [d.lower() for d in dirs]

        # make directories
        dirpath = self._fsname(dirs)
        if not os.path.isdir(dirpath):
            umask = os.umask(REPOSITORY_UMASK)
            try:
                os.makedirs(dirpath)
            finally:
                os.umask(umask)

        # generate file name
        fileformat = FILE_FORMAT
        # time/counter (%t)
        if string.find(fileformat, "%t")>=0:
            fileformat = string.replace(fileformat, "%t", "%c")
            counter = int(DateTime().strftime('%m%d%H%M%S'))
        else:
            counter = 0
        if string.find(fileformat, "%c")==-1:
            raise ValueError("Invalid file format '%s'" % FILE_FORMAT)
        # user (%u)
        if string.find(fileformat, "%u")>=0:
            if (getattr(self, 'REQUEST', None) is not None and
               self.REQUEST.has_key('AUTHENTICATED_USER')):
                user = getSecurityManager().getUser().getUserName()
                fileformat = string.replace(fileformat, "%u", user)
            else:
                fileformat = string.replace(fileformat, "%u", "")
        # path (%p)
        if string.find(fileformat, "%p")>=0:
            temp = string.joinfields(rel_url_list, "_")
            fileformat = string.replace(fileformat, "%p", temp)
        # file and extension (%n and %e)
        if string.find(fileformat,"%n")>=0 or string.find(fileformat,"%e")>=0:
            fileformat = string.replace(fileformat, "%n", id_name)
            fileformat = string.replace(fileformat, "%e", id_ext)

        # lock the directory
        if lock: self._dir__lock(dirpath)

        # search for unique filename
        if counter:
            fn = join(dirpath, string.replace(fileformat, "%c", ".%s" % counter))
        else:
            fn = join(dirpath, string.replace(fileformat, "%c", ''))
        while isfile(fn) or isfile(fn+'.undo') or isfile(fn+'.tmp'):
            counter = counter + 1
            fn = join(dirpath, string.replace(fileformat, "%c", ".%s" % counter))
        if counter:
            fileformat = string.replace(fileformat, "%c", ".%s" % counter)
        else:
            fileformat = string.replace(fileformat, "%c", '')

        dirs.append(fileformat)
        return dirs

    def _get_zodb_id(self):
        """ Returns the id of this object """
        return self.id

    def _get_zodb_path(self, parent=None):
        """ Returns the ZODB path of the parent object """
        if parent is None:
            parent = self.aq_parent

        if ZODB_PATH == VIRTUAL:
            path = parent.absolute_url(1).split('/')
        else:
            path = list(parent.getPhysicalPath())
        return filter(None, path)

    def _static_url(self, icon=0, preview=0):
        """ Return the static url of the file """
        static_path = os.environ.get('EXTFILE_STATIC_PATH')
        if static_path is not None:
            filename, content_type, icon, preview = \
                        self._get_file_to_serve(icon, preview)
            if icon:
                # cannot serve statically
                return '%s?icon=1' % self.absolute_url()
            else:
                # rewrite to static url
                static_host = os.environ.get('EXTFILE_STATIC_HOST')
                host = self.REQUEST.SERVER_URL
                if static_host is not None:
                    if host[:8] == 'https://':
                        host = 'https://' + static_host
                    else:
                        host = 'http://' + static_host
                host = host + urllib.quote(static_path) + '/'
                return host + urllib.quote('/'.join(filename))
        else:
            if icon:
                return '%s?icon=1' % self.absolute_url()
            elif preview:
                return '%s?preview=1' % self.absolute_url()
            else:
                return self.absolute_url()

    def _get_file_to_serve(self, icon=0, preview=0):
        """ Find out about the file we are going to serve """
        if not self._access_permitted():
            preview = 1
        if preview and not getattr(self, 'has_preview', 0):
            icon = 1

        if icon:
            filename = self._get_icon_file()
            content_type = 'image/gif'
        elif preview:
            filename = self.prev_filename
            content_type = self.prev_content_type
        else:
            filename = self.filename
            content_type = self.content_type

        return filename, content_type, icon, preview

    def _get_icon_file(self, broken=False):
        """ Returns the filesystem path of the icon corresponding
            to self.content_type. If broken is True, returns the
            filesystem path of the "broken" icon.
        """
        return join(here, self.getIconPath(broken))

    def _link(self, href, text, title=None, css_class=None, **args):
        """ Constructs an HTML link tag.
            Assumes all arguments are properly quoted.
        """
        result = '<a href="%s"' % (href,)
        if title is not None:
            result = '%s title="%s"' % (result, title)
        if css_class is not None:
            result = '%s class="%s"' % (result, css_class)
        for key in args.keys():
            value = args.get(key)
            if value:
                result = '%s %s="%s"' % (result, key, value)
        return '%s>%s</a>' % (result, text)

    def _bytetostring(self, value):
        """ Convert an int-value (file-size in bytes) to an String
            with the file-size in Byte, KB or MB
        """
        bytes = float(value)
        if bytes>=1000:
            bytes = bytes/1024
            if bytes>=1000:
                bytes = bytes/1024
                typ = ' MB'
            else:
                typ = ' KB'
        else:
            typ = ' Bytes'
        strg = '%4.2f'%bytes
        strg = strg[:4]
        if strg[3]=='.': strg = strg[:3]
        strg = strg+typ
        return strg

    def _changed(self, content_type, new_content_type):
        """ Return true if the content_type has changed (and we care) """
        return REPOSITORY_EXTENSIONS in (MIMETYPE_APPEND, MIMETYPE_REPLACE) and \
               content_type != new_content_type

    def _afterUpdate(self):
        """ Called whenever the file data has been updated.
            Fires an ExtFileUpdatedEvent.
        """
        self.ZCacheable_invalidate()
        event.notify(ExtFileUpdatedEvent(self))

    ################################
    # Special management methods   #
    ################################

    security.declarePrivate('get_fsname')
    def get_fsname(self):
        """ Returns the current file system path of the file or image.
            This path can be used to access the file even while a
            transaction is in progress (aka Zagy's revenge :-).
            Returns None if the file does not exist in the repository.
        """
        return self._get_fsname(self.filename)

    ################################
    # Repository locking methods   #
    ################################

    def _dir__lock(self, dir):
        """ Lock a directory """
        if hasattr(self, '_v_dir__lock'):
            raise DirLockError('Double lock in thread')
        self._v_dir__lock = DirLock(dir)

    def _dir__unlock(self):
        """ Unlock a previously locked directory """
        if hasattr(self, '_v_dir__lock'):
            self._v_dir__lock.release()
            delattr(self, '_v_dir__lock')

    ################################
    # Transaction manager methods  #
    ################################

    def _register(self):
        if _debug: logger.info('registering %s' % TM.contains(self))
        TM.register(self)
        if _debug: logger.info('registered %s' % TM.contains(self))

    def _begin(self):
        self._v_begin_called = 1    # for tests
        if _debug: logger.info('beginning %s' % self._get_zodb_id())

    def _finish(self):
        """ Commits the temporary file """
        self._v_finish_called = 1   # for tests
        TM.remove(self)             # for tests
        if self.filename:
            tmp_fn = self._temp_fsname(self.filename)
            if _debug: logger.info('finishing %s' % tmp_fn)
            if isfile(tmp_fn):
                if _debug: logger.info('isfile %s' % tmp_fn)
                fn = self._fsname(self.filename)
                if isfile(fn):
                    try:
                        os.remove(fn)
                    except OSError:
                        logger.error('_finish', exc_info=True)
                try:
                    os.rename(tmp_fn, fn)
                except OSError:
                    logger.error('_finish', exc_info=True)

    def _abort(self):
        """ Deletes the temporary file """
        self._v_abort_called = 1    # for tests
        TM.remove(self)             # for tests
        if self.filename:
            tmp_fn = self._temp_fsname(self.filename)
            if _debug: logger.info('aborting %s' % tmp_fn)
            if isfile(tmp_fn):
                if _debug: logger.info('isfile %s' % tmp_fn)
                try:
                    os.remove(tmp_fn)
                except OSError:
                    logger.error('_abort', exc_info=True)

InitializeClass(ExtFile)


# Event handlers
def afterClone(self, event):
    """ When a copy of the object is created (zope copy-paste-operation),
        this function is called by CopySupport.py. A copy of the external
        file is created and self.filename is changed.

        Subscriber for (IExtFile, IObjectClonedEvent)
    """
    # We have been copied, also copy the disk file
    fn = self._get_fsname(self.filename)
    if fn:
        self._register()    # Register with TM
        try:
            new_fn = self._get_new_ufn()
            self._update_data(fn, self._temp_fsname(new_fn))
            self.filename = new_fn
        finally:
            self._dir__unlock()


def afterAdd(self, event):
    """ This method is called, whenever _setObject in ObjectManager gets
        called. This is the case after a normal add and if the object is a
        result of cut-paste- or rename-operation. In the first case, the
        external files doesn't exist yet, otherwise it was renamed to .undo
        by beforeDelete before and must be restored by _undo().

        Subscriber for (IExtFile, IObjectMovedEvent)
    """
    from zope.app.container.interfaces import IObjectAddedEvent
    from zope.app.container.interfaces import IObjectRemovedEvent

    # If this is a Removed event we are done
    if IObjectRemovedEvent.providedBy(event):
        return

    # The disk file has been renamed to .undo by beforeDelete
    self._undo(self.filename)

    # If this is an Added event we are done
    if IObjectAddedEvent.providedBy(event):
        return

    # We have been moved, also move the disk file
    fn = self._get_fsname(self.filename)
    if fn:
        self._register()    # Register with TM
        try:
            new_fn = self._get_new_ufn()
            self._update_data(fn, self._temp_fsname(new_fn))
            self._delete(self.filename)
            self.filename = new_fn
        finally:
            self._dir__unlock()


def beforeDelete(self, event):
    """ This method is called, when the object is deleted. To support
        undo-functionality and because this happens too, when the object
        is moved (cut-paste) or renamed, the external file is not deleted.
        It is just renamed to filename.undo and remains in the
        repository, until it is deleted manually.

        Subscriber for (IExtFile, IObjectWillBeMovedEvent)
    """
    from OFS.interfaces import IObjectWillBeAddedEvent

    # If this is an Add event we are done
    if IObjectWillBeAddedEvent.providedBy(event):
        return

    # Delete the disk file, i.e. rename it to .undo
    self._delete(self.filename)


# Filename -> id translation
bad_chars =  """ ,;:'"()[]{}ÄÅÁÀÂÃäåáàâãÇçÉÈÊËÆéèêëæÍÌÎÏíìîïÑñÖÓÒÔÕØöóòôõøŠšßÜÚÙÛüúùûÝŸýÿŽž"""
good_chars = """____________AAAAAAaaaaaaCcEEEEEeeeeeIIIIiiiiNnOOOOOOooooooSssUUUUuuuuYYyyZz"""
TRANSMAP = string.maketrans(bad_chars, good_chars)

def normalize_id(id):
    # Support at least utf-8 and latin-1 filenames.
    # This is lame, but before it was latin-1 only.
    try:
        uid = unicode(id, 'utf-8')
    except UnicodeError, TypeError:
        try:
            uid = unicode(id, 'iso-8859-15')
        except UnicodeError, TypeError:
            return id
    id = uid.encode('iso-8859-15', 'ignore')
    id = string.translate(id, TRANSMAP)
    return id


# Copy-of protection
copy_of_re = re.compile('(^(copy[0-9]*_of_)+)')

def copy_of_protect(id):
    match = copy_of_re.match(id)
    if match is not None:
        id = id[len(match.group(1)):]
    return id


# File extensions
def guess_extension(type, strict=True):
    type = type.lower()
    extension = config.mimetypes_override_map.get(type)
    if extension is not None:
        return extension
    return mimetypes.guess_extension(type, strict)


# FileUpload factory
from cgi import FieldStorage
from ZPublisher.HTTPRequest import FileUpload

def HTTPUpload(fp, content_type=None, filename=None):
    """ Create a FileUpload instance from a file handle (and content_type) """
    if isinstance(fp, FileUpload):
        if content_type:
            fp.headers['content-type'] = content_type
    else:
        environ = {'REQUEST_METHOD': 'POST'}
        if content_type:
            environ['CONTENT_TYPE'] = content_type
        elif hasattr(fp, 'headers') and fp.headers.has_key('content-type'):
            environ['CONTENT_TYPE'] = fp.headers['content-type']
        fp = FileUpload(FieldStorage(fp, environ=environ))
    if filename:
        fp.filename = filename
    return fp


# Pdata to tempfile
def pdata(file):
    temp_file = TemporaryFile()
    data, next = file.data, file.next
    temp_file.write(data)
    while next is not None:
        data, next = next.data, next.next
        temp_file.write(data)
    temp_file.seek(0)
    return temp_file


# Repository lock
class DirLockError(OSError):
    pass

class DirLock:
    """ Manage the lockfile for a directory """

    lock_name = '@@@lock'

    def __init__(self, dir):
        self._lock = os.path.join(dir, self.lock_name)
        for i in range(config.dirlock_sleep_count):
            if self.islocked():
                logger.debug("Waiting for lock %s" % self._lock)
            else:
                return self._mklock()
            time.sleep(config.dirlock_sleep_seconds)
        else:
            logger.error("Failed to get lock %s" % self._lock)
            raise DirLockError("Failed to get lock %s" % self._lock)

    def release(self):
        self._rmlock()

    def islocked(self):
        os.path.exists(self._lock)

    def _mklock(self):
        f = open(self._lock, 'wt')
        f.write('ExtFile directory lock. This file should only exist for short periods of time.')
        f.close()

    def _rmlock(self):
        os.remove(self._lock)


# Stream iterator
class stream_iterator(object):
    if issubclass(IStreamIterator, interface.Interface):
        interface.implements(IStreamIterator)
    else:
        # old-stye zope interface (before ZCA)
        __implements__ = (IStreamIterator,)

    def __init__(self, stream, blocksize=2<<16):
        self._stream = stream
        self._blocksize = blocksize

    def next(self):
        data = self._stream.read(self._blocksize)
        if not data:
            self._stream.close()
            self._stream = None
            raise StopIteration
        return data

    def __len__(self):
        cur_pos = self._stream.tell()
        self._stream.seek(0, 2)
        size = self._stream.tell()
        self._stream.seek(cur_pos, 0)
        return size

    def __nonzero__(self):
        return self.__len__() and 1 or 0

    def __del__(self):
        if self._stream is not None:
            self._stream.close()
