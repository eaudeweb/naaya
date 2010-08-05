###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import os, tempfile
from interfaces import IConverter

class BaseConverterError(Exception): pass

class TmpFile:

    def __init__(self, data):
        self.fname = tempfile.mktemp()
        open(self.fname,'w+b').write(data)

    def __str__(self): return self.fname
    __repr__ = __str__

    def __del__(self):
        os.unlink(self.fname)
	

class BaseConverter:
    """ Base class for all converters """

    content_type = None
    content_description = None

    __implements__ = IConverter.ConverterInterface

    def __init__(self):
        if not self.content_type:
            raise BaseConverterError,'content_type undefinied'

        if not self.content_description:
            raise BaseConverterError,'content_description undefinied'


    def execute(self,com):

        try:
            import win32pipe
            return win32pipe.popen(com).read()

        except ImportError:
            return os.popen(com).read()

    def saveFile(self, data):
        return TmpFile(data)

    def getDescription(self):   return self.content_description
    def getType(self):          return self.content_type
    def getDependency(self):    return getattr(self,'depends_on','')
    def __call__(self, s):      return self.convert(s)
    
