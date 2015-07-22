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

__version__='1.5.6'

from Products.ZCatalog.CatalogPathAwareness import CatalogAware
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from OFS.Cache import Cacheable
from Globals import HTMLFile, MessageDialog, InitializeClass, package_home
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl import Permissions
from Acquisition import aq_acquire
from mimetypes import guess_extension
from webdav.Lockable import ResourceLockedError
from webdav.common import rfc1123_date
from DateTime import DateTime
import urllib, os, string, types, sha, base64
from os.path import join, isfile
from tempfile import TemporaryFile
from Products.ExtFile import TM

from webdav.WriteLockInterface import WriteLockInterface
from IExtFile import IExtFile

from zLOG import *
_SUBSYS = 'ExtFile'
_debug = 0

try: import Zope2
except ImportError: ZOPE28 = 0
else: ZOPE28 = 1

try: from zope.contenttype import guess_content_type
except ImportError:
    try: from zope.app.content_types import guess_content_type
    except ImportError: from OFS.content_types import guess_content_type

try: from zExceptions import Redirect
except ImportError: Redirect = 'Redirect'

try: from ZPublisher.Iterators import IStreamIterator
except ImportError: IStreamIterator = None

ViewPermission = Permissions.view
AccessPermission = Permissions.view_management_screens
ChangePermission = 'Change ExtFile/ExtImage'
DownloadPermission = 'Download ExtFile/ExtImage'

import re
copy_of_re = re.compile('(^(copy[0-9]*_of_)+)')

from Config import *

manage_addExtFileForm = HTMLFile('dtml/extFileAdd', globals()) 


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
        the uploaded file externally in a repository-direcory. """

    __implements__ = (IExtFile, WriteLockInterface)
    
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
    
    # location of the file-repository
    _repository = REPOSITORY_PATH
    
    # make sure the download permission is available
    security.setPermissionDefault(DownloadPermission, ('Manager',))
    
    # the above does not work in Zope < 2.8
    if not ZOPE28:
        security.declareProtected(DownloadPermission, '_dummy')

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
    
    def __str__(self):
        return self.index_html()
    
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
                if last_mod > 0 and last_mod < mod_since:
                    # Set headers for Apache caching
                    last_mod = rfc1123_date(self._p_mtime)
                    REQUEST.RESPONSE.setHeader('Last-Modified', last_mod)
                    REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
                    # RFC violation. See http://collector.zope.org/Zope/544
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
                    as_attachment=False,
                    REQUEST=None):
        """Return the file with it's corresponding MIME-type.

            @param as_attachment: if not None, return the file as an attachment
                                  using its title or id as a suggested filename;
                                  see RFC 2616 section 19.5.1 for more details
        """

        if REQUEST is not None:
            if self._if_modified_since_request_handler(REQUEST):
                self.ZCacheable_set(None)
                return ''

            if self._redirect_default_view_request_handler(icon, preview, REQUEST):
                return ''

        filename, content_type, icon, preview = self._get_file_to_serve(icon, preview)
        filename = self._get_fsname(filename)

        if _debug > 1: LOG(_SUBSYS, INFO, 'serving %s, %s, %s, %s' %(filename, content_type, icon, preview))

        cant_read_exc = "Can't read: "
        if filename:
            try: size = os.stat(filename)[6]
            except: raise cant_read_exc, ("%s (%s)" %(self.id, filename))
        else:
            filename = join(package_home(globals()), 'icons', 'broken.gif')
            try: size = os.stat(filename)[6]
            except: raise cant_read_exc, ("%s (%s)" %(self.id, filename))
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

        close_data = 1
        try:
            if REQUEST is not None:
                last_mod = rfc1123_date(self._p_mtime)
                if as_attachment:
                    REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s"' % (self.title_or_id(),))
                REQUEST.RESPONSE.setHeader('Last-Modified', last_mod)
                REQUEST.RESPONSE.setHeader('Content-Type', content_type)
                REQUEST.RESPONSE.setHeader('Content-Length', size)
                self.ZCacheable_set(None)

                # Support Zope 2.7.1 IStreamIterator
                if IStreamIterator is not None:
                    close_data = 0
                    return stream_iterator(data)

                blocksize = 2<<16
                while 1:
                    buffer = data.read(blocksize)
                    REQUEST.RESPONSE.write(buffer)
                    if len(buffer) < blocksize:
                        break
                return ''
            else:
                return data.read()
        finally:
            if close_data: data.close()
    
    security.declareProtected(ViewPermission, 'view_image_or_file')
    def view_image_or_file(self):
        """ The default view of the contents of the File or Image. """
        raise Redirect, self.absolute_url()

    security.declareProtected(ViewPermission, 'link')
    def link(self, text='', **args):
        """ Return a HTML link tag to the file """
        if text=='': text = self.title_or_id()
        strg = '<a href="%s"' % (self._static_url())
        for key in args.keys():
            value = args.get(key)
            strg = '%s %s="%s"' % (strg, key, value)
        strg = '%s>%s</a>' % (strg, text)
        return strg
    
    security.declareProtected(ViewPermission, 'icon_gif')
    def icon_gif(self):
        """ Return an icon for the file's MIME-Type """
        raise Redirect, self._static_url(icon=1)
    
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
    def getIconPath(self):
        """ Depending on the MIME Type of the file/image an icon
            can be displayed. This function determines which
            image in the lib/python/Products/ExtFile/icons/...
            directory shold be used as icon for this file/image
        """
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
            return join('icons', cat, file)
        return join('icons', self._types['default'])
    
    security.declareProtected(ViewPermission, 'static_url')
    def static_url(self, icon=0, preview=0):
        """ Returns the static url of the file """
        return self._static_url(icon, preview)
                    
    security.declareProtected(ViewPermission, 'static_mode')
    def static_mode(self):
        """ Returns true if serving static urls """
        return os.environ.get('EXTFILE_STATIC_PATH') is not None

    security.declareProtected(AccessPermission, 'get_filename')
    def get_filename(self):
        """ Returns the filename as file system path. 
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
    manage_main = HTMLFile('dtml/extFileEdit', globals())    
    
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
    manage_uploadForm = HTMLFile('dtml/extFileUpload', globals())
    
    security.declareProtected(ChangePermission, 'manage_upload')
    def manage_upload(self, file='', content_type='', REQUEST=None):
        """ Upload file from file handle or string buffer """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
                            
        if type(file) == types.StringType:
            temp_file = TemporaryFile()
            temp_file.write(file)
            temp_file.seek(0)
        else:
            temp_file = file
        return self.manage_file_upload(temp_file, content_type, REQUEST)

    security.declareProtected(ChangePermission, 'manage_file_upload')
    def manage_file_upload(self, file='', content_type='', REQUEST=None):
        """ Upload file from file handle or local directory """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
                            
        if type(file) == types.StringType:
            cant_read_exc = "Can't open: "
            try: file = open(file, 'rb')
            except: raise cant_read_exc, file
        if content_type:
            file = HTTPUpload(file, content_type)
        self.content_type = self._get_content_type(file, file.read(100), 
                            self.id, self.content_type)
        file.seek(0)
        self._register()    # Register with TM
        try:
            new_fn = self._get_ufn(self.filename)
            self._update_data(file, self._temp_fsname(new_fn))
        finally:
            self._dir__unlock()
        self.filename = new_fn
        self._afterUpdate()
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, manage_tabs_message='Upload complete.')                

    security.declareProtected(ChangePermission, 'manage_http_upload')
    def manage_http_upload(self, url, REQUEST=None):
        """ Upload file from http-server """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
                            
        url = urllib.quote(url,'/:')
        cant_read_exc = "Can't open: "
        try: file = urllib.urlopen(url)
        except: raise cant_read_exc, url
        file = HTTPUpload(file)
        self.content_type = self._get_content_type(file, file.read(100),
                            self.id, self.content_type)
        file.seek(0)
        self._register()    # Register with TM
        try:
            new_fn = self._get_ufn(self.filename)
            self._update_data(file, self._temp_fsname(new_fn))
        finally:
            self._dir__unlock()
        self.filename = new_fn
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
        self.content_type = self._get_content_type(file, file.read(100),
                            self.id, self.content_type)
        file.seek(0)
        self._register()    # Register with TM
        try:
            # Need to pass in the path as webdav.NullResource calls PUT
            # on an unwrapped object.
            try:
                self.aq_parent # This raises AttributeError if no context
            except AttributeError:
                path = self._get_zodb_path(REQUEST.PARENTS[0])
            else:
                path = None
            new_fn = self._get_ufn(self.filename, path=path)
            self._update_data(file, self._temp_fsname(new_fn))
        finally:
            self._dir__unlock()
        self.filename = new_fn
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
        if type(infile) == types.ListType:
            infile = self._fsname(infile)
        if type(outfile) == types.ListType:
            outfile = self._fsname(outfile)
        try:
            self._copy(infile, outfile)
        except:
            if isfile(outfile): # This is always a .tmp file
                try: os.remove(outfile)
                except OSError: pass
            raise
        else:
            self.http__refreshEtag()
    
    def _copy(self, infile, outfile):
        """ Read binary data from infile and write it to outfile
            infile and outfile may be strings, in which case a file with that
            name is opened, or filehandles, in which case they are accessed
            directly.
        """
        if type(infile) is types.StringType: 
            try:
                instream = open(infile, 'rb')
            except IOError:
                raise IOError, ("%s (%s)" %(self.id, infile))
            close_in = 1
        else:
            instream = infile
            close_in = 0
        if type(outfile) is types.StringType: 
            umask = os.umask(REPOSITORY_UMASK)
            try:
                outstream = open(outfile, 'wb')
                os.umask(umask)
                self._dir__unlock()   # unlock early
            except IOError:
                os.umask(umask)
                raise IOError, ("%s (%s)" %(self.id, outfile))
            close_out = 1
        else:
            outstream = outfile
            close_out = 0
        try:
            blocksize = 2<<16
            block = instream.read(blocksize)
            outstream.write(block)
            while len(block)==blocksize:
                block = instream.read(blocksize)
                outstream.write(block)
        except IOError:
            raise IOError, ("%s (%s)" %(self.id, filename))
        try: instream.seek(0)
        except: pass
        if close_in: instream.close()
        if close_out: outstream.close()
    
    def _undo(self):
        """ Restore filename after delete or copy-paste """
        fn = self._fsname(self.filename)
        if not isfile(fn) and isfile(fn+'.undo'): 
            self._register()    # Register with TM
            os.rename(fn+'.undo', self._temp_fsname(self.filename))
    
    def _fsname(self, filename):
        """ Generates the full filesystem name, incuding directories from 
            self._repository and filename
        """
        path = [INSTANCE_HOME]
        path.extend(self._repository)
        if type(filename) == types.ListType:
            path.extend(filename)
        elif filename != '':
            path.append(filename)
        return apply(join, path)

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
        self._undo()
        if isfile(tmp_fn):
            return tmp_fn

    # b/w compatibility
    def _get_filename(self, filename):
        """ Deprecated, use _get_fsname """
        return self._get_fsname(filename)

    def _get_ufn(self, filename, path=None, content_type=None, lock=1):
        """ If no unique filename has been generated, generate one
            otherwise, return the existing one.
        """
        if UNDO_POLICY==ALWAYS_BACKUP or filename==[]: 
            new_fn = self._get_new_ufn(path=path, content_type=content_type, lock=lock)
        else: 
            new_fn = filename[:]
        if filename:
            old_fn = self._fsname(filename)
            if UNDO_POLICY==ALWAYS_BACKUP: 
                try: os.rename(old_fn, old_fn+'.undo')
                except OSError: pass
            else:
                try: os.rename(old_fn+'.undo', old_fn)
                except OSError: pass
        return new_fn

    def _get_new_ufn(self, path=None, content_type=None, lock=1):
        """ Create a new unique filename """
        id = self.id

        # hack so the files are not named copy_of_foo
        if COPY_OF_PROTECTION:
            match = copy_of_re.match(id)
            if match is not None:
                id = id[len(match.group(1)):]

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
                if mime_ext in ('.jpeg', '.jpe'): 
                    mime_ext = '.jpg'   # for IE/Win :-(
                if mime_ext in ('.obj',):
                    mime_ext = '.exe'   # b/w compatibility
                if mime_ext in ('.tiff',):
                    mime_ext = '.tif'   # b/w compatibility
                # don't change extensions of unknown binaries
                if not (content_type == 'application/octet-stream' and id_ext):
                    if REPOSITORY_EXTENSIONS == MIMETYPE_APPEND:
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
            mkdir_exc = "Can't create directory: "
            umask = os.umask(REPOSITORY_UMASK)
            try:
                os.makedirs(dirpath)
                os.umask(umask)
            except:
                os.umask(umask)
                raise mkdir_exc, dirpath

        # generate file name
        fileformat = FILE_FORMAT
        # time/counter (%t)
        if string.find(fileformat, "%t")>=0:
            fileformat = string.replace(fileformat, "%t", "%c")
            counter = int(DateTime().strftime('%m%d%H%M%S'))
        else:
            counter = 0
        invalid_format_exc = "Invalid file format: "
        if string.find(fileformat, "%c")==-1:
            raise invalid_format_exc, FILE_FORMAT
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
            filename = join(package_home(globals()), self.getIconPath())
            content_type = 'image/gif'
        elif preview:
            filename = self.prev_filename
            content_type = self.prev_content_type
        else:
            filename = self.filename
            content_type = self.content_type
        
        return filename, content_type, icon, preview

    def _get_zodb_path(self, parent=None):
        """ Returns the ZODB path of the parent object """
        # XXX: The Photo product uploads into unwrapped ExtImages.
        # As we can not reliably guess our parent object we fall back
        # to the old behavior. This means that Photos will always
        # use ZODB_PATH = VIRTUAL independent of config settings.
        try:
            from Products.Photo.ExtPhotoImage import PhotoImage
        except ImportError:
            pass
        else:
            if isinstance(self, PhotoImage):
                path = self.absolute_url(1).split('/')[:-1]
                return filter(None, path)
        # XXX: End of hack

        # For normal operation objects must be wrapped
        if parent is None:
            parent = self.aq_parent

        if ZODB_PATH == VIRTUAL:
            path = parent.absolute_url(1).split('/')
        else:
            path = list(parent.getPhysicalPath())
        return filter(None, path)

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
        
    def _afterUpdate(self):
        """ Called whenever the file data has been updated. 
            Invokes the manage_afterUpdate() hook.
        """
        self.ZCacheable_invalidate()

        return self.manage_afterUpdate(self._get_fsname(self.filename), 
                                       self.content_type, self.get_size())
        
    ################################
    # Special management methods   #
    ################################
    
    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, item, new_fn=None):
        """ When a copy of the object is created (zope copy-paste-operation),
            this function is called by CopySupport.py. A copy of the external 
            file is created and self.filename is changed.
        """
        call_afterUpdate = 0
        try: 
            self.aq_parent # This raises AttributeError if no context
        except AttributeError: 
            self._v_has_been_cloned=1   # This is to make webdav COPY work
        else:
            fn = self._get_fsname(self.filename)
            if fn:
                self._register()    # Register with TM
                try:
                    new_fn = new_fn or self._get_new_ufn()
                    self._update_data(fn, self._temp_fsname(new_fn))
                    self.filename = new_fn
                    call_afterUpdate = 1
                finally:
                    self._dir__unlock()
                if call_afterUpdate:
                    self._afterUpdate()
        return ExtFile.inheritedAttribute("manage_afterClone")(self, item)
        
    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        """ This method is called, whenever _setObject in ObjectManager gets 
            called. This is the case after a normal add and if the object is a 
            result of cut-paste- or rename-operation. In the first case, the
            external files doesn't exist yet, otherwise it was renamed to .undo
            by manage_beforeDelete before and must be restored by _undo().
        """
        self._undo()
        if hasattr(self, "_v_has_been_cloned"):
            delattr(self, "_v_has_been_cloned")
            self.manage_afterClone(item)
        return ExtFile.inheritedAttribute("manage_afterAdd")(self, item, container)
    
    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. To support 
            undo-functionality and because this happens too, when the object 
            is moved (cut-paste) or renamed, the external file is not deleted. 
            It is just renamed to filename.undo and remains in the 
            repository, until it is deleted manually.
        """
        tmp_fn = self._temp_fsname(self.filename)
        fn = self._fsname(self.filename)
        if isfile(tmp_fn):
            try: os.rename(tmp_fn, fn+'.undo')
            except OSError: pass
            else:
                try: os.remove(fn)
                except OSError: pass
        elif isfile(fn):
            try: os.rename(fn, fn+'.undo')
            except OSError: pass
        return ExtFile.inheritedAttribute("manage_beforeDelete")(self, item, container)

    security.declarePrivate('manage_afterUpdate')
    def manage_afterUpdate(self, filename, content_type, size):
        """ This method is called whenever the file data has been updated.
            May be overridden by subclasses to perform additional operations.
            The 'filename' argument contains the path as returned by get_fsname().
        """
        pass

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
            raise DirLockError, 'Double lock in thread'
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
        if _debug: LOG(_SUBSYS, INFO, 'registering %s' % TM.contains(self))
        TM.register(self)
        if _debug: LOG(_SUBSYS, INFO, 'registered %s' % TM.contains(self))

    def _begin(self):
        self._v_begin_called = 1    # for tests
        if _debug: LOG(_SUBSYS, INFO, 'beginning %s' % self.id) 

    def _finish(self):
        """ Commits the temporary file """
        self._v_finish_called = 1   # for tests
        TM.remove(self)             # for tests
        if self.filename:
            tmp_fn = self._temp_fsname(self.filename)
            if _debug: LOG(_SUBSYS, INFO, 'finishing %s' % tmp_fn) 
            if isfile(tmp_fn):
                if _debug: LOG(_SUBSYS, INFO, 'isfile %s' % tmp_fn) 
                fn = self._fsname(self.filename)
                try: os.remove(fn)
                except OSError: pass
                os.rename(tmp_fn, fn)

    def _abort(self):
        """ Deletes the temporary file """
        self._v_abort_called = 1    # for tests
        TM.remove(self)             # for tests
        if self.filename:
            tmp_fn = self._temp_fsname(self.filename)
            if _debug: LOG(_SUBSYS, INFO, 'aborting %s' % tmp_fn) 
            if isfile(tmp_fn):
                if _debug: LOG(_SUBSYS, INFO, 'isfile %s' % tmp_fn) 
                try: os.remove(tmp_fn)
                except OSError: pass

InitializeClass(ExtFile)


# Filename to id translation
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


# Repository lock
import time

class DirLockError(OSError): 
    pass

class DirLock:
    """ Manage the lockfile for a directory """

    lock_name = '@@@lock'
    sleep_secs = 1.5
    sleep_times = 10

    def _mklock(self):
        f = open(self._lock, 'wt') 
        f.write('ExtFile dir lock. You may want to remove this file.')
        f.close()

    def _rmlock(self):
        os.remove(self._lock)

    def islocked(self):
        os.path.isfile(self._lock)

    def release(self):
        self._rmlock()

    def __init__(self, dir):
        self._lock = os.path.join(dir, self.lock_name)
        for i in range(self.sleep_times):
            if self.islocked():
                LOG(_SUBSYS, BLATHER, "Waiting for lock '%s'" % self._lock)
                time.sleep(self.sleep_secs)
            else:
                self._mklock()
                break
        else:
            LOG(_SUBSYS, BLATHER, "Failed to get lock '%s'" % self._lock)
            raise DirLockError, "Failed to get lock '%s'" % self._lock


# Stream iterator
if IStreamIterator is not None:

    class stream_iterator:
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

