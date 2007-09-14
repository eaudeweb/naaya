###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
WinWord converter

$Id: doc.py,v 1.13 2004/10/18 16:00:00 ajung Exp $
"""

import os, sys

from Globals import package_home
from Products.TextIndexNG2.BaseConverter import BaseConverter

wvConf_file = os.path.join(package_home(globals()), 'wvText.xml')

class Converter(BaseConverter):

    content_type = ('application/msword','application/ms-word','application/vnd.ms-word')
    content_description = "Microsoft Word"
    depends_on = 'wvWare'

    def convert(self, doc):
        """Convert WinWord document to raw text"""
        
        tmp_name = self.saveFile(doc)
        if sys.platform == 'win32':
            return self.execute('wvWare -c utf-8 --nographics -x "%s" "%s" 2> nul:' % (wvConf_file, tmp_name))
        else:
            return self.execute('wvWare -c utf-8 --nographics -x "%s" "%s" 2> /dev/null' % (wvConf_file, tmp_name))

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'utf-8'
