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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania

import os
import sys
import tempfile

class TmpFile:

    def __init__(self, data):
        self.fname = tempfile.mktemp()
        open(self.fname,'w+b').write(data)

    def __str__(self): return self.fname
    __repr__ = __str__

    def __del__(self):
        os.unlink(self.fname)

class Converter:

    content_type = 'text/xml'
    content_description = 'xslt'
    depends_on = 'xsltproc'

    def __call__(self, doc, style):
        return self.convert(doc, style)

    def execute(self, com):
        try:
            import win32pipe
            return win32pipe.popen(com).read()
        except ImportError:
            return os.popen(com).read()

    def saveFile(self, data):
        return TmpFile(data)

    def convert(self, doc, style):
        """Convert XML document to HTML document"""
        xml_name = self.saveFile(doc)
        style_name = self.saveFile(style)
        if sys.platform == 'win32':
            html2xml = self.execute('tidy.exe -latin1 -asxhtml -bare "%s" 2> null:' % xml_name)
        else:
            html2xml = self.execute('tidy -latin1 -asxhtml -bare %s 2> /dev/null' % xml_name)

        xml_buf = self.saveFile(html2xml)
        if sys.platform == 'win32':
            html = self.execute('xsltproc.exe "%s" "%s"' % (style_name, xml_buf))
        else:
            html = self.execute('xsltproc "%s" "%s" 2> /dev/null' % (style_name, xml_buf))
        return html

    def convert2(self, doc, style, encoding, mimetype):
        return self.convert(doc, style), 'utf-8'

    def getDescription(self):
        return self.content_description

    def getType(self):
        return self.content_type

    def getDependency(self):
        return getattr(self,'depends_on','')