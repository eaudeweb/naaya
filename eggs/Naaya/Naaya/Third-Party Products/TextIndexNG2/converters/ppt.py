###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
PowerPoint converter

$Id: ppt.py,v 1.13 2004/09/08 20:20:12 ajung Exp $
"""

import sys
from Products.TextIndexNG2.BaseConverter import BaseConverter
from stripogram import html2text


class Converter(BaseConverter):

    content_type = ('application/mspowerpoint', 'application/ms-powerpoint', 
                'application/vnd.ms-powerpoint')
    content_description = "Microsoft PowerPoint"
    depends_on = 'pptHtml'

    def convert(self, doc):
        """Convert PowerPoint document to raw text"""
        
        tmp_name = self.saveFile(doc)
        if sys.platform == 'win32':
            html = self.execute('ppthtml "%s" 2> nul:' % tmp_name)
        else:
            html = self.execute('ppthtml "%s" 2> /dev/null' % tmp_name)

        return html2text(html,
                         ignore_tags=('img',),
                         indent_width=4,
                         page_width=80)

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'iso-8859-15'
