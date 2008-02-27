# Make this an External Method

from Products.ExtFile.ExtImage import ExtImage

def toExtImage(self, id, backup=0):
	'''Converts plain Image to ExtImage. 
	   Call this method in the Folder context and pass the id.
	   Must have threads, will not work in debugger!'''
	oldId = str(id)
	oldOb = self._getOb(oldId)
	newId = oldId+'___tmp'
	ximOb = ExtImage(oldId, oldOb.title)
	newId = self._setObject(newId, ximOb)
	newOb = self._getOb(newId)
	newOb.manage_http_upload(oldOb.absolute_url())	
	newOb.content_type = oldOb.content_type
	if backup: self.manage_renameObjects([oldId], [oldId+'_bak'])
	else: self.manage_delObjects([oldId])
	self.manage_renameObjects([newId], [oldId])

