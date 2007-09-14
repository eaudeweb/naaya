###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
pdf converter

$Id: pdf.py,v 1.12 2004/03/16 06:40:49 ajung Exp $
"""

from Products.TextIndexNG2.BaseConverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/pdf',)
    content_description = "Adobe Acrobat PDF"
    depends_on = 'pdftotext'

    def convert(self, doc):
        raise NotImplementedError

    def convert2(self, doc, encoding, mimetype):
        """Convert pdf data to raw text"""
        tmp_name = self.saveFile(doc)
        return self.execute('pdftotext -enc UTF-8 "%s" -' % tmp_name), 'utf-8'
