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
from DateTime import DateTime

#Product imports
from Products.NaayaBase.NyFSFile import NyFSFile
from constants import *

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
        self.review_date = DateTime()
        self.store_kwargs(kwargs)
        NyFSFile.__init__(self, id, title, file)
        self.ratings = {}
        self.votes = 0

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
        self.linecomments = kwargs.get('adt_comment', '')

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'saveRate')
    def saveRate(self, REQUEST=None):
        """ """
        rate_lists = self.getRateLists()
        for r in rate_lists:
            if REQUEST.has_key(r.id):
                self.ratings[r.title] = REQUEST[r.id]
                self.votes += 1
        self._p_changed = 1
        REQUEST.RESPONSE.redirect('%s/reviews_index_html' % self.get_consultation_url())

    security.declareProtected(PERMISSION_REVIEW_CONSULTATION, 'save_properties')
    def save_properties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        if self.REQUEST.AUTHENTICATED_USER.getUserName() == self.contributor:
            self.store_kwargs(kwargs)
            self.handleUpload(kwargs.get('file', ''))
            self.setSessionInfo(['Saved changes.'])
        else:
            self.setSessionErrors(['You are not the owner of this Review'])

        self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit_html')

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'getRatings')
    def getRatings(self):
        output = {}
        rate_lists = self.getRateLists()
        if self.votes == 0:
            return None
        else:
            for r in rate_lists:
                procent = 0
                if r.title in self.ratings.keys():
                    try:
                        buf = [o.id for o in r.get_list()]
                        val = buf.index(self.ratings[r.title]) + 1
                        procent = val*100/len(r.get_list())
                    except:
                        return None
                output[r.title] = procent
            return output

    def get_cr_file(self, REQUEST, RESPONSE):
        """Download the attached file"""
        
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.utToUtf8(self.filename))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return self.index_html()

    def get_review_date(self):
        """ """
        return self.review_date

    security.declareProtected(PERMISSION_REVIEW_CONSULTATION, 'get_question_answer')
    def get_question_answer(self, qid):
        for k,v in self.answers:
            if k == qid:
                return v

    security.declareProtected(PERMISSION_MANAGE_CONSULTATION, 'getAnswersDict')
    def getAnswersDict(self):
        """ """
        ans_dict = {}
        for q in self.answers:
            qid, ans = q[0], q[1]
            ans_dict[qid] = ans
        return ans_dict

    security.declareProtected(PERMISSION_REVIEW_CONSULTATION, 'edit_html')

    edit_html = PageTemplateFile('zpt/review_edit', globals())
    rate_review_html = PageTemplateFile('zpt/review_rate', globals())

InitializeClass(ConsultationReviewItem)
