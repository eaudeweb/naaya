# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

#Product imports
from Products.NaayaBase.NyFSFile import NyFSFile

def addSimpleConsultationComment(self, title='', contributor='', contributor_name='', message='', file='', REQUEST=None):
    """ """
    
    id = 'scc' + self.utGenRandomId(6)
    if REQUEST and not contributor:
        contributor = REQUEST.AUTHENTICATED_USER.getUserName()
    
    ob = SimpleConsultationComment(id, title, contributor, contributor_name, message, file)
    self._setObject(id, ob)
    
    ob = self._getOb(id)
    ob.handleUpload(file)
    
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_simpleconsultation_comment?status=ok')

class SimpleConsultationComment(NyFSFile):
    """ """
    
    meta_type = 'Simple Consultation Comment'
    
    manage_options = ()
    
    security = ClassSecurityInfo()
    
    def __init__(self, id, title, contributor, contributor_name, message, file):
        self.contributor = contributor
        self.contributor_name = contributor_name
        self.message = message
        self.comment_date = DateTime()
        NyFSFile.__init__(self, id, title, file)
        
    def handleUpload(self, file=None):
        if not file: return
        self.filename = file.filename
        data, size = self._read_data(file)
        content_type = self._get_content_type(file, data, self.__name__, 'application/octet-stream')
        self.update_data(data, content_type, size, file.filename)

    def get_scc_file(self, REQUEST, RESPONSE):
        """Download the attached file"""
        
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.utToUtf8(self.filename))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return self.index_html()

    def get_comment_date(self):
        """ """
        return self.comment_date

InitializeClass(SimpleConsultationComment)
