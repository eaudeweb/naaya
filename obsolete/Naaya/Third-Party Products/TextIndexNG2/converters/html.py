###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
a stupid HTML to Ascii converter

$Id: html.py,v 1.17 2004/09/08 20:20:12 ajung Exp $
"""

from Products.TextIndexNG2.BaseConverter import BaseConverter
from entities import convert_entities
from stripogram import html2text


class Converter(BaseConverter):

    content_type = ('text/html',)
    content_description = "Converter HTML to ASCII"

    def convert(self, html):
        """Convert html data to raw text"""
        
        return html2text(html,
                         ignore_tags=('img',),
                         indent_width=0,
                         page_width=256)
         
    def convert2(self, doc, encoding, mimetype):
        # convert to unicode
        if not isinstance(doc, unicode):
            doc = unicode(doc, encoding, 'replace')
        doc = convert_entities(doc)
        result = self.convert(doc)
        # convert back to utf-8
        return result.encode('utf-8'), 'utf-8'
