###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
A stupid HTML to Ascii converter

$Id: sgml.py,v 1.8 2004/07/03 10:37:57 ajung Exp $
"""

import re
from Products.TextIndexNG2.BaseConverter import BaseConverter
from StripTagParser import StripTagParser
from entities import convert_entities

encoding_reg = re.compile('encoding="(.*?)"')

class Converter(BaseConverter):

    content_type = ('text/sgml', 'text/xml')
    content_description = "Converter SGML to ASCII"

    def convert(self, doc):
        """Convert html data to raw text"""

        p = StripTagParser()
        p.feed(doc)
        p.close()
        return str(p)

    def convert2(self, doc, encoding, mimetype):

        # Use encoding from XML preamble if present
        mo = encoding_reg.search(doc)
        if mo:
            encoding = mo.group(1)
        
        if not isinstance(doc, unicode):
            doc = unicode(doc, encoding, 'replace')
        doc = convert_entities(doc)
        doc = doc.encode('utf-8')
        return self.convert(doc), 'utf-8'
