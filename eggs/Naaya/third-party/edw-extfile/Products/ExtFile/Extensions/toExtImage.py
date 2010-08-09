#
# Make this an External Method
#
# Id:            toExtImage
# Title:
# Module Name:   ExtFile.toExtImage
# Function Name: toExtImage
#

from Products.ExtFile.ExtImage import ExtImage

def toExtImage(self, id, backup=0):
    '''Converts OFS.Image to ExtImage.
       Call this method in the Folder context and pass the id
       of the Image to convert.
    '''
    oldId = str(id)
    self.manage_renameObject(oldId, oldId+'.bak')
    oldOb = self._getOb(oldId+'.bak')
    newOb = ExtImage(oldId, oldOb.title)
    newId = self._setObject(oldId, newOb)
    newOb = self._getOb(newId)
    newOb.manage_upload(oldOb.data, oldOb.content_type)
    if not int(backup):
        self._delObject(oldId+'.bak')
    return newId
