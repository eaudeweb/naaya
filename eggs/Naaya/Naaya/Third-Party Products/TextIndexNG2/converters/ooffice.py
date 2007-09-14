###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
a simple OpenOffice converter 

$Id: ooffice.py,v 1.8 2004/09/08 20:20:12 ajung Exp $
"""

import xml.sax
import zipfile, cStringIO
from xml.sax.handler import ContentHandler

from Products.TextIndexNG2.BaseConverter import BaseConverter


class ootextHandler(ContentHandler):

    def characters(self, ch):
        self._data.write(ch.encode("utf-8") + ' ')

    def startDocument(self):
        self._data = cStringIO.StringIO()

    def getxmlcontent(self, doc):

        file = cStringIO.StringIO(doc)

        doctype = """<!DOCTYPE office:document-content PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">"""
        xmlstr = zipfile.ZipFile(file).read('content.xml')
        xmlstr = xmlstr.replace(doctype,'')       
        return xmlstr

    def getData(self):
        return self._data.getvalue()


class Converter(BaseConverter):

    content_type = ('application/vnd.sun.xml.writer',)
    content_description = "OpenOffice"

    def convert(self, doc):
        """ convert OpenOffice Document """

        handler = ootextHandler()
        xmlstr = handler.getxmlcontent(doc)
        xml.sax.parseString(xmlstr, handler)
        return handler.getData()

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'utf-8'
