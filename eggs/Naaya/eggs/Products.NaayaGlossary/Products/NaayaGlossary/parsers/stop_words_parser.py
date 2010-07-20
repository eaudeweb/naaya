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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Ghica Alexandru, Finsiel Romania


from xml.sax.handler import ContentHandler
from xml.sax import *
from cStringIO import StringIO


class stop_words_struct:
    """ """
    def __init__(self, text):
        """ """
        self.text = text

class stop_words_handler(ContentHandler):
    """ """

    def __init__(self):
        """ """
        self.stop_words = []

    def startElement(self, name, attrs):
        """ """
        if name == 'word':
            self.stop_words.append(stop_words_struct(attrs['text'].encode('latin-1')))

    def endElement(self, name):
        """ """
        pass

class stop_words_parser:
    """ """

    def parseContent(self, content):
        """ """
        handler = stop_words_handler()
        parser = make_parser()
        parser.setContentHandler(handler)
        inpsrc = InputSource()
        inpsrc.setByteStream(StringIO(content))
        try:
            parser.parse(inpsrc)
            return (handler, '')
        except Exception, error:
            return (None, error)