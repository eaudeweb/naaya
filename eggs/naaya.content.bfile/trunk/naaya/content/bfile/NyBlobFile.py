"""Storage and provider of blob files"""

# from zope.interface import implements
from ZODB.POSException import POSKeyError
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from DateTime.DateTime import DateTime
from OFS.Cache import Cacheable
from OFS.SimpleItem import Item
from Persistence import Persistent
from ZODB.blob import Blob
from ZODB.interfaces import BlobError
from ZPublisher.HTTPRangeSupport import parseRange, expandRanges
from ZPublisher.Iterators import IStreamIterator
from ZPublisher.Iterators import filestream_iterator
from interfaces import INyBlobFile
from os import fstat
from webdav.common import rfc1123_date
from zope.interface import implements
from zope.interface.interfaces import IInterface
import mimetypes
import os
import urllib

from utils import strip_leading_underscores

COPY_BLOCK_SIZE = 65536  # 64KB


def contentDispositionHeader(disposition, charset='utf-8', language=None,
                             **kw):
    """Return a properly quoted disposition header

    Originally from CMFManagedFile/content.py. charset default changed to
    utf-8 for consistency with the rest of Archetypes.
    """

    from email.Message import Message as emailMessage

    for key, value in kw.items():
        # stringify the value
        if isinstance(value, unicode):
            value = value.encode(charset)
        else:
            value = str(value)
            # raise an error if the charset doesn't match
            unicode(value, charset, 'strict')
        # if any value contains 8-bit chars, make it an
        # encoding 3-tuple for special treatment by
        # Message.add_header() (actually _formatparam())
        try:
            unicode(value, 'us-ascii', 'strict')
        except UnicodeDecodeError:
            value = (charset, language, value)

    m = emailMessage()
    m.add_header('content-disposition', disposition, **kw)
    return m['content-disposition']


def handleIfModifiedSince(instance, REQUEST, RESPONSE):
    # HTTP If-Modified-Since header handling: return True if
    # we can handle this request by returning a 304 response
    header = REQUEST.get_header('If-Modified-Since', None)
    if header is not None:
        header = header.split(';')[0]
        # Some proxies seem to send invalid date strings for this
        # header. If the date string is not valid, we ignore it
        # rather than raise an error to be generally consistent
        # with common servers such as Apache (which can usually
        # understand the screwy date string as a lucky side effect
        # of the way they parse it).
        # This happens to be what RFC2616 tells us to do in the face of an
        # invalid date.
        try:
            mod_since = long(DateTime(header).timeTime())
        except:
            mod_since = None
        if mod_since is not None:
            if instance._p_mtime:
                last_mod = long(instance._p_mtime)
            else:
                last_mod = long(0)
            if last_mod > 0 and last_mod <= mod_since:
                RESPONSE.setStatus(304)
                return True


def handleRequestRange(instance, length, REQUEST, RESPONSE):
    # check if we have a range in the request
    ranges = None
    range = REQUEST.get_header('Range', None)
    request_range = REQUEST.get_header('Request-Range', None)
    if request_range is not None:
        # Netscape 2 through 4 and MSIE 3 implement a draft version
        # Later on, we need to serve a different mime-type as well.
        range = request_range
    if_range = REQUEST.get_header('If-Range', None)
    if range is not None:
        ranges = parseRange(range)
        if if_range is not None:
            # Only send ranges if the data isn't modified, otherwise send
            # the whole object. Support both ETags and Last-Modified dates!
            if len(if_range) > 1 and if_range[:2] == 'ts':
                # ETag:
                if if_range != instance.http__etag():
                    # Modified, so send a normal response. We delete
                    # the ranges, which causes us to skip to the 200
                    # response.
                    ranges = None
            else:
                # Date
                date = if_range.split(';')[0]
                try:
                    mod_since = long(DateTime(date).timeTime())
                except:
                    mod_since = None
                if mod_since is not None:
                    if instance._p_mtime:
                        last_mod = long(instance._p_mtime)
                    else:
                        last_mod = long(0)
                    if last_mod > mod_since:
                        # Modified, so send a normal response. We delete
                        # the ranges, which causes us to skip to the 200
                        # response.
                        ranges = None
            RESPONSE.setHeader('Accept-Ranges', 'bytes')
        if ranges and len(ranges) == 1:
            [(start, end)] = expandRanges(ranges, length)
            size = end - start
            RESPONSE.setHeader('Content-Length', size)
            RESPONSE.setHeader(
                'Content-Range',
                'bytes %d-%d/%d' % (start, end - 1, length))
            RESPONSE.setStatus(206)  # Partial content
            return dict(start=start, end=end)
    return {}


def openBlob(blob, mode='r'):
    """ open a blob taking into consideration that it might need to be
        invalidated in order to be fetch again via zeo;  please see
        http://dev.plone.org/plone/changeset/32170/ for more info """
    try:
        return blob.open(mode)
    except IOError:
        blob._p_deactivate()
        return blob.open(mode)


class BlobStreamIterator(object):
    """ a streamiterator for blobs enabling to directly serve them
        in an extra ZServer thread """
    if IInterface.providedBy(IStreamIterator):  # is this zope 2.12?
        implements(IStreamIterator)
    else:
        __implements__ = (IStreamIterator,)

    def __init__(self, blob, mode='r', streamsize=1 << 16, start=0, end=None):
        self.blob = openBlob(blob, mode)
        self.streamsize = streamsize
        self.start = start
        self.end = end
        self.seek(start, 0)

    def next(self):
        """ return next chunk of data from the blob, taking the optionally
            given range into consideration """
        if self.end is None:
            bytes = self.streamsize
        else:
            bytes = max(min(self.end - self.tell(), self.streamsize), 0)
        data = self.blob.read(bytes)
        if not data:
            raise StopIteration
        return data

    def __len__(self):
        return fstat(self.blob.fileno()).st_size

    def __iter__(self):
        return self

    # bbb methods to pretend we're a file-like object

    def close(self):
        return self.blob.close()

    def read(self, *args, **kw):
        return self.blob.read(*args, **kw)

    def seek(self, *args, **kw):
        return self.blob.seek(*args, **kw)

    def tell(self):
        return self.blob.tell()


class NyBlobFile(Item, Persistent, Cacheable, Implicit):
    """Naaya persistence of file using ZODB blobs"""

    implements(INyBlobFile)
    meta_type = "NyBlobFile"
    security = ClassSecurityInfo()

    def __init__(self, **kwargs):
        super(NyBlobFile, self).__init__(**kwargs)
        kwargs.setdefault('filename', None)
        kwargs.setdefault('content_type', 'application/octet-stream')
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self._blob = Blob()

    def is_broken(self):
        filename = self.get_filename()
        if not filename:
            return True
        try:
            os.stat(filename)
            return False
        except (OSError, POSKeyError):
            return True

    def open(self):
        return self._blob.open('r')

    def open_iterator(self):
        return filestream_iterator(self._blob.committed(), 'rb')

    def open_write(self):
        return self._blob.open('w')

    def send_data(self, RESPONSE, as_attachment=True, set_filename=True,
                  REQUEST=None):
        """NyBlobFiles can also be served using X-Sendfile.
        In order to do so, you need to set X-NaayaEnableSendfile header
        to "on" by frontend server for each request.

        Lighttpd.conf example (working in proxy mode)::
         server.modules  += ( "mod_setenv" )
         setenv.add-request-header = ( "X-NaayaEnableSendfile" => "on" )
         proxy-core.allow-x-sendfile = "enable"

        """
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Type', self.content_type)
        if as_attachment:
            header_value = "attachment"
            if set_filename:
                utf8_fname = urllib.quote(self.filename)
                header_value += ";filename*=UTF-8''%s" % utf8_fname
            RESPONSE.setHeader('Content-Disposition', header_value)

        # Test for enabling of X-SendFile
        if REQUEST is not None:
            ny_xsendfile = REQUEST.get_header("X-NaayaEnableSendfile")
            if ny_xsendfile is not None and ny_xsendfile == "on":
                RESPONSE.setHeader("X-Sendfile", self._current_filename())
                return "[body should be replaced by front-end server]"

        if hasattr(RESPONSE, '_streaming'):
            return self.open_iterator()
        else:
            return self.open().read()

    def _current_filename(self):
        """ Convenience function that returns blob's filename """
        try:
            return self._blob.committed()
        except POSKeyError:
            return None
        except BlobError:
            return self._blob._p_blob_uncommitted

    get_filename = _current_filename

    def __repr__(self):
        return '<%(cls)s %(fname)r (%(mime)s, %(size)r bytes)>' % {
            'cls': self.__class__.__name__,
            'fname': self.filename,
            'mime': self.content_type,
            'size': self.size,
        }

    def get_size(self):
        return self.size

    security.declareProtected("View", 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None, charset='utf-8',
                   disposition='inline'):
        """ make it directly viewable when entering the objects URL """

        if REQUEST is None:
            REQUEST = self.REQUEST

        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

        if handleIfModifiedSince(self, REQUEST, RESPONSE):
            return ''

        length = self.get_size()
        RESPONSE.setHeader('Content-Length', length)

        filename = self.getFilename()
        if filename is not None:
            if not isinstance(filename, unicode):
                filename = unicode(filename, charset, errors="ignore")
            filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
                filename)
            header_value = contentDispositionHeader(
                disposition=disposition,
                filename=filename)
            RESPONSE.setHeader("Content-disposition", header_value)

        request_range = handleRequestRange(self, length, REQUEST, RESPONSE)
        for fr in self._blob.readers:
            self._blob.readers.remove(fr)

        return self.getIterator(**request_range)

    security.declarePrivate('getIterator')

    def getIterator(self, **kw):
        """ return a filestream iterator object from the blob """
        return BlobStreamIterator(self._blob, **kw)

    def getContentType(self):
        return self.content_type

    def getFilename(self):
        return self.filename

    def raw_data(self):
        f = self.open()
        s = f.read()
        f.close()
        for fr in self._blob.readers:
            self._blob.readers.remove(fr)
        return s

    def write_data(self, data, content_type=None):
        if content_type:
            self.content_type = content_type

        if isinstance(data, basestring):
            blob = self.open_write()
            blob.write(data)
            blob.seek(0)
            blob.close()
            self.size = len(data)
            return self

        bf_stream = self.open_write()
        size = 0
        while True:
            _data = data.read(COPY_BLOCK_SIZE)
            if not _data:
                break
            bf_stream.write(_data)
            size += len(_data)
        bf_stream.close()
        self.size = size
        return self


def make_blobfile(the_file, **kwargs):
    filename = strip_leading_underscores(trim_filename(the_file.filename))

    content_type = mimetypes.guess_type(the_file.filename)[0]
    if content_type is None:
        content_type = getattr(the_file, 'headers', {}).get(
            'content-type', 'application/octet-stream')

    meta = {
        'filename': filename,
        'content_type': content_type,
    }
    meta.update(kwargs)

    blobfile = NyBlobFile(**meta)

    # copy file data
    bf_stream = blobfile.open_write()
    size = 0
    the_file.seek(0)
    while True:
        data = the_file.read(COPY_BLOCK_SIZE)
        if not data:
            break
        bf_stream.write(data)
        size += len(data)
    bf_stream.close()
    blobfile.size = size

    return blobfile


def trim_filename(filename):
    """
    Internet Explorer sends us the complete file path, not just the
    file's name, so we need to strip that.
    """
    return filename.rsplit('\\', 1)[-1]
