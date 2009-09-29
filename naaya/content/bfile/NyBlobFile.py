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
