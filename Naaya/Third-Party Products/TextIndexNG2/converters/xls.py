###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Excel Converter

$Id: xls.py,v 1.6 2004/09/08 20:20:12 ajung Exp $
"""

import sys
from Products.TextIndexNG2.BaseConverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/msexcel','application/ms-excel','application/vnd.ms-excel')
    content_description = "Microsoft Excel"
    depends_on = 'xls2csv'

    def convert(self, doc):
        """Convert Excel document to raw text"""

        tmp_name = self.saveFile(doc)
        if sys.platform == 'win32':
            return self.execute('xls2csv -d 8859-1 -q 0 "%s" 2> nul:' % tmp_name)
        else:
            return self.execute('xls2csv -d 8859-1 -q 0 "%s" 2> /dev/null' % tmp_name)

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'iso-8859-15'
