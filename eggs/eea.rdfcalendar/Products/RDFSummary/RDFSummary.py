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
# The Original Code is RDFSummary version 1.0.
#
# The Initial Developer of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Soren Roug, EEA
# Dominique Dutoit, European Commission
# Tomas Hjelmberg, CMG
# URAGO Keisuke, <bravo@resourcez.org> - for slash code
# David Chandek-Stark for RSS 2.0 additions in known_items.
# Histoshi Igarashi for fail-tolerance in end_image and unknown_endtag
# Keisuke Urago for content module
#
#
#
# $Id$
#
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from DateTime import *
import binascii
from hashlib import md5 as _md5_func
import operator, time
from persistent import Persistent
import Acquisition
from zope.datetime import rfc1123_date
import AccessControl
from AccessControl.rolemanager import RoleManager
import OFS
try:
    from Products.ZCatalog.CatalogAwareness import CatalogAware
except ImportError:
    class CatalogAware:
        def reindex_object(self): pass
from App.config import getConfiguration
from App.special_dtml import DTMLFile

import pickle, types, os
from os.path import join, isfile

from copy import deepcopy
from .rdfparser import RDFParser


CONFIG = getConfiguration()
CONFIG.environment.update(os.environ)
try:
    _repos = join(CONFIG.clienthome, 'RDFSummary')
except Exception:
    _repos = join(os.environ.get('CLIENT_HOME', '.'), 'RDFSummary')
_repos = getattr(CONFIG, 'environment', {}).get('rdfsummary_repo', _repos)

fixslash = str.maketrans('/','-')


class RDFSummary (
    CatalogAware,
    Acquisition.Implicit,
    Persistent,
    RoleManager,
    OFS.SimpleItem.Item):
    "Retrieve RDF Summaries from other websites."

    # Declare the security
    #
    security=ClassSecurityInfo()

#   security.setPermissionDefault('Change RDFSummaries',('Manager',))

    manage_options=(
        {'label':'Properties', 'action':'manage_main'},
        {'label':'View', 'action':''},
        {'label':'Update', 'action':'update'},
        {'label':'Source', 'action':'show_source'},
        ) + OFS.SimpleItem.SimpleItem.manage_options

    meta_type = 'RDF Summary'

    security.declareProtected('View', 'index_html')

    index_html = DTMLFile("htmlview", globals())

    security.declareProtected('View', 'show_source')

    show_source = DTMLFile("source", globals())

    security.declareProtected('View management screens', 'manage_main')

    manage_main = DTMLFile("edit_prop", globals())

    security.declareProtected('View', 'channel')

    def channel(self):
        "Return channel dictionary"
        return self._v_channel

    security.declareProtected('View', 'textinput')

    def textinput(self):
        "Text input dictionary"
        return self._v_textinput

    security.declareProtected('View', 'image')

    def image(self):
        "Return the image"
        return self._v_image

    security.declareProtected('View', 'items')

    def items(self):
        "Return the list of items"
        pp = self.physicalpath(self._filename)
        if isfile(pp) and self._v_mtime != os.stat(pp)[8]:
            self._loadpickles()
        return self._v_items

    security.declareProtected('View', 'rdfsource')

    def rdfsource(self):
        "Return the RDF source"
        return self._v_rdfsource

    security.declarePublic('filename')

    def filename(self):
        "Return the filename"
        return self._filename

    security.declarePublic('lastupdated')

    def lastupdated(self):
        "Return the date last updated"
        if self._v_updatedate is not None:
            return DateTime(self._v_updatedate)
        else:
            return None

    def __init__(self, id, title, rssurl, http_proxy, fetchimage):
        self.id = id
        self.title = title
        self.rssurl = rssurl
        self.http_proxy = http_proxy
        self.fetchimage = fetchimage
        self._filename = '' # Signal manage_afterAdd we're new

        #relevant information about the feed
        self.feed_gone = None
        self.feed_etag = None
        self.feed_status = None
        self.feed_version = None
        self.feed_bozo_exception = None
        self.feed_encoding = None
        self.feed_modified = None

        self._v_updatedate = None
        self._v_textinput = {}
        self._v_channel = {}
        self._v_image = {}
        self._v_items = []
        self._v_rdfsource = None
        self._v_mtime = None

    def __setstate__(self,state):
        #restore object
        Persistent.__setstate__(self, state)
        if not hasattr(self, "_filename"): # backwards compatibility
            self._filename = self.id

        if not hasattr(self, "feed_etag"):
            self.feed_etag = None
        if not hasattr(self, "feed_gone"):
            self.feed_gone = None
        if not hasattr(self, "lastmodified"):
            self.lastmodified = None
        if not hasattr(self, "feed_status"):
            self.feed_status = None
        if not hasattr(self, "feed_version"):
            self.feed_version = None
        if not hasattr(self, "feed_bozo_exception"):
            self.feed_bozo_exception = None
        if not hasattr(self, "feed_encoding"):
            self.feed_encoding = None
        if not hasattr(self, "feed_modified"):
            self.feed_modified = None

        if not hasattr(self, "fetchimage"): # backwards compatibility
            self.fetchimage = "yes"
        self._loadpickles()

    def _loadpickles(self):
        try:
            pp = self.physicalpath(self._filename)
            f = open(pp, 'rb')
            self._v_mtime = os.stat(pp)[8]
            # latin1 reads pickles written by Python 2
            load = lambda f: pickle.load(f, encoding='latin1')
            self._v_updatedate = load(f)
            self._v_textinput = load(f)
            self._v_channel = load(f)
            self._v_image = load(f)
            self._v_items = load(f)
            self._v_rdfsource = load(f)
            self.feed_gone = load(f)
            self.feed_etag = load(f)
            self.feed_status = load(f)
            self.feed_version = load(f)
            self.feed_bozo_exception = load(f)
            self.feed_encoding = load(f)
            self.feed_modified = load(f)
            f.close()
        except (EOFError, SystemError, IOError, pickle.UnpicklingError, ValueError):
            self._v_updatedate = None
            self._v_textinput = {}
            self._v_channel = {}
            self._v_image = {}
            self._v_items = []
            self._v_rdfsource = None
            self._v_mtime = None

    security.declareProtected('Change RDFSummaries', 'manage_edit')

    def manage_edit(self, title, rssurl, http_proxy, updateonchg='off',
                    fetchimage='no', REQUEST=None):
        """ Edits the summary's characteristics
        """
        self.title = title
        self.rssurl = rssurl
        self.http_proxy = http_proxy
        self.fetchimage = fetchimage

        if updateonchg == "on":
            self.reindex_object()
            return self.update(REQUEST)
        else:
            if REQUEST:
                message="Properties changed"
                return self.manage_main(self,REQUEST,manage_tabs_message=message)

    ################################
    ##        Public methods       #
    ################################

    security.declareProtected('View', 'update')

    def update(self,REQUEST=None):
        """ Call this function to get it to update its content
        """
        # make the directories
        if not os.path.isdir(_repos):
            try:
                os.makedirs(_repos)
            except:
                raise OSError('Can\'t create directory %s' %_repos)
        self._v_updatedate = time.time()
        p = RDFParser(self.http_proxy, self.fetchimage)
        p.parse_url(self.rssurl, self.feed_etag, self.feed_modified, REQUEST)

        # channel and at least one item is required in all supported RSS-versions

        if p.feed_status == 304:
            if REQUEST:
                message=""" The feed has not changed since you last checked """
                return self.manage_main(self,REQUEST,manage_tabs_message=message)
        elif p.feed_status == 301:
            buf = self.rssurl
            self.rssurl = p.feed_redirect
            self._p_changed = 1
            if REQUEST:
                message=""" The feed from %s was permanently moved to %s""" % (buf, self.rssurl) 
                return self.manage_main(self,REQUEST,manage_tabs_message=message)

        if p.channel != {}:
            self.feed_gone = p.feed_gone
            self.feed_etag = p.feed_etag
            self.feed_status = p.feed_status
            self.feed_version = p.feed_version
            self.feed_bozo_exception = p.feed_bozo_exception
            self.feed_encoding = p.feed_encoding
            self.feed_modified = p.feed_modified
            self._v_textinput = deepcopy(p.textinput)
            self._v_channel = deepcopy(p.channel)
            self._v_image = deepcopy(p.image)
            self._v_items = deepcopy(p.items)
            self._v_rdfsource = p.rdfsource
        else:
            if REQUEST:
                message="""Error updating %s.
                Channel element is required.""" % self.id
                return self.manage_main(self,REQUEST,manage_tabs_message=message)
        fn = self.physicalpath(self._filename)
        try:
            os.rename(fn, fn+'.undo')
        except OSError:
            pass

        #write object
        f = open(fn, 'wb')
        pickle.dump(self._v_updatedate, f)
        pickle.dump(self._v_textinput, f)
        pickle.dump(self._v_channel, f)
        pickle.dump(self._v_image, f)
        pickle.dump(self._v_items, f)
        pickle.dump(self._v_rdfsource, f)

        pickle.dump(self.feed_gone, f)
        pickle.dump(self.feed_etag, f)
        pickle.dump(self.feed_status, f)
        pickle.dump(self.feed_version, f)
        pickle.dump(self.feed_bozo_exception, f)
        pickle.dump(self.feed_encoding, f)
        pickle.dump(self.feed_modified, f)
        f.close()

        if REQUEST:
            message='Content of %s has been updated.' % self.id
            return self.manage_main(self,REQUEST,manage_tabs_message=message)

    security.declareProtected('View', 'picture')

    def picture(self):
        """ Make a img element that displays the picture
        """
        if 'data' in self._v_image:
            lstart=''
            lend=''
            if 'link' in self._v_image:
                lstart='<a href="%s">' % self._v_image['link']
                lend='</a>'
            alt=''
            if 'title' in self._v_image:
                alt='alt="%s" ' % self._v_image['title']
            return ('%s<img src="%s/view_image" border="0" %s/>%s' %
                    ( lstart, self.absolute_url(), alt, lend ))

    security.declareProtected('View', 'view_image')

    def view_image(self, REQUEST, RESPONSE):
        """ The default view of the contents of an Image.

            Returns the contents of the file or image.  Also, sets the
            Content-Type HTTP header to the objects content type.
        """
        # HTTP If-Modified-Since header handling.
        header=REQUEST.get_header('If-Modified-Since', None)
        if header is not None:
            header=header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:    mod_since=int(DateTime(header).timeTime())
            except: mod_since=None
            last_mod = 0
            if mod_since is not None:
                if self._p_mtime:
                    last_mod = int(self._p_mtime)
                else:
                    last_mod = 0
            if last_mod > 0 and last_mod <= mod_since:
                # Set header values since apache caching will return Content-Length
                # of 0 in response if size is not set here
                RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
                RESPONSE.setHeader('Content-Type', self._v_image['content_type'])
                RESPONSE.setHeader('Content-Length', self._v_image['size'])
                RESPONSE.setStatus(304)
                return ''

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
        RESPONSE.setHeader('Content-Type', self._v_image['content_type'])
        RESPONSE.setHeader('Content-Length', self._v_image['size'])

        data=self._v_image['data']
        if type(data) is type(''): return data

        while data is not None:
            RESPONSE.write(data.data)
            data=data.next

        return ''

    ################################
    ##       Private methods       #
    ################################

    def _copy(self, infile, outfile):
        """ Read binary data from infile and write it to outfile
            infile and outfile my be strings, in which case a file with that
            name is opened, or filehandles, in which case they are accessed
            directly.
        """
        if type(infile) is str:
            try:
                instream = open(infile, 'rb')
            except IOError:
                self._undo()
                try:
                    instream = open(infile, 'rb')
                except IOError:
                    raise IOError("%s (%s)" %(self.id, infile))
            close_in = 1
        else:
            instream = infile
            close_in = 0
        if type(outfile) is str:
            try:
                outstream = open(outfile, 'wb')
            except IOError:
                raise IOError("%s (%s)" %(self.id, outfile))
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
            raise IOError("%s (%s)" %(self.id, filename))
        try: instream.seek(0)
        except: pass
        if close_in: instream.close()
        if close_out: outstream.close()

    def _undo(self):
        """ Restore filename after undo or copy-paste """
        if self._filename == '':
            return
        fn = self.physicalpath(self._filename)
        if not isfile(fn) and isfile(fn+'.undo'):
                os.rename(fn+'.undo', fn)
        self._loadpickles()

    def _get_new_ufn(self):
        """ Create a new unique filename, drop the last newline
            The base64 set of characters are listed in rfc1341. Unfortunately
            it includes the / character, and I must deal with that in UNIX systems.
        """
        url = self.absolute_url(1)
        if isinstance(url, str):
            url = url.encode('utf-8')
        digest = _md5_func(url).digest()
        return binascii.b2a_base64(digest).decode('ascii').translate(fixslash).strip()

    def physicalpath(self, filename=''):
        """ Generate the full filename, including directories from
            _repos and self._filename
        """
        path = _repos
        if type(filename)==list:
            for item in filename:
                path = join(path,item)
        elif filename != '':
            path = join(path,filename)
        return path

    ################################
    ## Special management methods  #
    ################################

    def manage_afterAdd(self, item, container, new_fn=None):
        """ This method is called, whenever _setObject in ObjectManager gets
            called. This is the case after a normal add and if the object is a
            result of cut-paste- or rename-operation.

            If it is a fresh add, then we don't want to load obsolete pickles from
            an old object with the same name, but if it is a cut-n-paste job, then
            the new object should load the pickles.
        """
        new_fn = new_fn or self._get_new_ufn()
        if self._filename != '':
            old_fn = self.physicalpath(self._filename)
            if isfile(old_fn):
                self._copy(old_fn, self.physicalpath(new_fn))
            else:
                if isfile(old_fn+'.undo'):
                    self._copy(old_fn+'.undo', self.physicalpath(new_fn))
            self._loadpickles()
        else:
            try:
                os.unlink(new_fn)
            except OSError:
                pass
        self._filename = new_fn
        return RDFSummary.inheritedAttribute ("manage_afterAdd") \
                (self, item, container)

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. To support
            undo-functionality and because this happens too, when the object
            is moved (cut-paste) or renamed, the external file is not deleted.
            It is just renamed to filename.undo and remains in the
            repository, until it is deleted manually.
        """
        fn = self.physicalpath(self._filename)
        try:
            os.unlink(fn+'.undo')
        except OSError:
            pass
        try:
            os.rename(fn, fn+'.undo')
        except OSError:
            pass
        return RDFSummary.inheritedAttribute ("manage_beforeDelete") \
               (self, item, container)

    def manage_undo_transactions(self, transaction_info, REQUEST=None):
        """ This method is called, when the user has chosen an Undo-action.
            To support undo-functionality the external file is just renamed back from
            filename.undo to filename.
        """
        fn = self.physicalpath(self._filename)
        try:
            os.rename(fn+'.undo', fn)
            self._loadpickles()
        except OSError:
            pass
        return RDFSummary.inheritedAttribute ("manage_undo_transactions") \
               (self, transaction_info, REQUEST)

# Initialize the class in order the security assertions be taken into account
#
InitializeClass(RDFSummary)

def manage_addRDFSummary(self, id, title, rssurl, http_proxy, fetchimage, REQUEST=None):
    """ Create a summary and install it in its parent Folder.
        The argument 'self' will be bound to the parent Folder.
    """
    summary = RDFSummary(id, title, rssurl, http_proxy,fetchimage )
    self._setObject(id, summary)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

manage_addRDFSummaryForm = DTMLFile('add_summary', globals())
