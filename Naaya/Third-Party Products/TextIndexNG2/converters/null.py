###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
a stupid null converter

$Id: null.py,v 1.9 2005/02/20 12:13:31 ctheune Exp $
"""

from Products.TextIndexNG2.BaseConverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('text/plain',)
    content_description = "Null converter"

    def convert(self, doc):
        return doc

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), encoding
