#
# Make this an External Method
#
# Id:            PUT_factory
# Title:
# Module Name:   ExtFile.PUT_factory
# Function Name: PUT_factory
#

from OFS.Image import getImageInfo
from Products.ExtFile.ExtImage import ExtImage
import string

def PUT_factory(self, name, typ, body):
    '''Creates ExtImage instead of plain Image.'''
    ct, w, h = getImageInfo(body)
    if ct:
        major, minor = string.split(ct, '/')
        if major == 'image':
            return ExtImage(name, '', '')
    major, minor = string.split(typ, '/')
    if major == 'image':
        return ExtImage(name, '', '')
    return None
