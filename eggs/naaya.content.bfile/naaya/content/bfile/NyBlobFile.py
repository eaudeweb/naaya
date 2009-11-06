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

    def send_data(self, RESPONSE):
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Disposition',
            "attachment;filename*=UTF-8''%s" % urllib.quote(self.filename))

        if not hasattr(RESPONSE, '_streaming'):
            return self.open().read()
        return self.open_iterator()

def make_blobfile(the_file, **kwargs):
    content_type = getattr(the_file, 'headers', {}).get(
        'content-type', 'application/octet-stream')

    meta = {
        'filename': the_file.filename,
        'content_type': content_type,
    }
    meta.update(kwargs)

    blobfile = NyBlobFile(**meta)

    # copy file data
    bf_stream = blobfile.open_write()
    data = the_file.read()
    bf_stream.write(data) # TODO: copy data in chunks
    bf_stream.close()
    blobfile.size = len(data)

    return blobfile
