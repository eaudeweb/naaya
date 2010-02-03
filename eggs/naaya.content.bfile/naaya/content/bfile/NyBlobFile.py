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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web
# David Batranu, Eau de Web

import urllib

from ZODB.blob import Blob
from Persistence import Persistent
from ZPublisher.Iterators import filestream_iterator

COPY_BLOCK_SIZE = 65536 # 64KB

class NyBlobFile(Persistent):
    """
    Naaya container for files stored using ZODB Blob
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        kwargs.setdefault('content_type', 'application/octet-stream')
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self._blob = Blob()

    def open(self):
        return self._blob.open('r')

    def open_iterator(self):
        return filestream_iterator(self._blob.committed(), 'rb')

    def open_write(self):
        return self._blob.open('w')

    def send_data(self, RESPONSE, as_attachment=True, set_filename=True):
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Type', self.content_type)
        if as_attachment:
            header_value = "attachment"
            if set_filename:
                utf8_fname = urllib.quote(self.filename)
                header_value += ";filename*=UTF-8''%s" % utf8_fname
            RESPONSE.setHeader('Content-Disposition', header_value)

        if not hasattr(RESPONSE, '_streaming'):
            return self.open().read()
        return self.open_iterator()

def make_blobfile(the_file, **kwargs):
    content_type = getattr(the_file, 'headers', {}).get(
        'content-type', 'application/octet-stream')

    meta = {
        'filename': trim_filename(the_file.filename),
        'content_type': content_type,
    }
    meta.update(kwargs)

    blobfile = NyBlobFile(**meta)

    # copy file data
    bf_stream = blobfile.open_write()
    size = 0
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
