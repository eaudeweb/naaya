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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaBase.NyFSFile import NyFSFile

def addConsultationReviewItem(self, contributor, contributor_name, file, kwargs):
    """ """
    
    id = 'cr' + self.utGenRandomId(6)
    title = contributor_name
    
    ob = ConsultationReviewItem(id, title, contributor, contributor_name, file, kwargs)
    self._setObject(id, ob)
    
    ob = self._getOb(id)
    ob.handleUpload(file)

class ConsultationReviewItem(NyFSFile):
    """ """
    
    meta_type = 'Consultation Review'
    
    manage_options = ()
    
    security = ClassSecurityInfo()
    
    def __init__(self, id, title, contributor, contributor_name, file, kwargs):
        self.contributor = contributor
        self.contributor_name = contributor_name
        self.store_kwargs(kwargs)
        NyFSFile.__init__(self, id, title, file)
        
    def handleUpload(self, file=None):
        if not file: return
        self.filename = file.filename
        data, size = self._read_data(file)
        content_type = self._get_content_type(file, data, self.__name__, 'application/octet-stream')
        self.update_data(data, content_type, size, file.filename)

    def store_kwargs(self, kwargs):
        #store answers
        self.answers = [(key, value) for key, value in kwargs.items() if key.startswith('q')]
        
        #store line comments
        self.linecomments = kwargs['adt_comment']

    def get_cr_file(self, REQUEST, RESPONSE):
        """Download the attached file"""
        
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.utToUtf8(self.filename))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return self.index_html()

    review_index_html = PageTemplateFile('zpt/review_index', globals())

InitializeClass(ConsultationReviewItem)
