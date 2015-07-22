###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Postscript converter

$Id: ps.py,v 1.9 2004/03/16 06:05:27 ajung Exp $
"""

from Products.TextIndexNG2.BaseConverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/postscript',)
    content_description = "Adobe Postscript Document"
    depends_on = 'ps2ascii'

    def convert(self, doc):
        """Convert postscript data to raw text"""
        
        tmp_name = self.saveFile(doc)
        return self.execute('ps2ascii "%s" -' % tmp_name)

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'iso-8859-15'
