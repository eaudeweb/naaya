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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency. All
# Rights Reserved.
#
# Authors:
# Alexandru Ghica, Adriana Baciu - Finsiel Romania


#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

#Product related imports
from Products.Finshare.DocBase import DocBase
from Products.Finshare.Constants import *
from Products.Finshare.DocHistory import DocHistory
from Products.Finshare.DocComments import DocComments


manage_addDocURL_html = PageTemplateFile('zpt/DocURL/url_manage_add', globals())
manage_addDocURL_html.FormAction = 'addDocURL'

def addDocURL(self, id='', title='', description='',abstract='', releasedate='', creationdate='', ownerinfo='', approved='', language='', coverage='', keywords='', sortorder='', author='', source='', locator='', REQUEST=None, **kwargs):
    """ add a new DocURL object """
    #id = self.utCleanupId(id)
    #if not id:
    id = 'url' + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = 100
    #if self.checkPermissionPublishObjects():
    approved = 1
    #else: approved = 0
    if not releasedate: releasedate = self.utGetTodayDate()
    else: releasedate = self.utConvertStringToDateTimeObj(releasedate)
    creationdate = self.utGetTodayDate()
    ownerinfo = self.getAuthenticatedUser()
    ob = DocURL(id, title, description, abstract, creationdate, releasedate, ownerinfo, language, coverage, keywords, sortorder, approved, author, source, locator)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.createHistory(HISTORY_ADD)
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'manage_addDocURL_html' or l_referer.find('manage_addDocURL_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'url_add_html':
            REQUEST.RESPONSE.redirect(self.absolute_url(0) + '/note_html')


class DocURL(DocBase, SimpleItem, DocHistory, DocComments):
    """ DocURL class """

    meta_type = METATYPE_DMURL
    icon = 'misc_/Finshare/url'
    icon_marked = 'misc_/Finshare/url_marked'

    manage_options = (
        DocBase.manage_options
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self,id, title, description, abstract, creationdate, releasedate, ownerinfo, language, coverage, keywords, sortorder, approved, author, source, locator):
        """ constructor """
        self.id = id
        self.title = title
        self.description = description
        self.abstract = abstract
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.ownerinfo = ownerinfo
        self.locator = locator
        self.releasedate = releasedate
        DocHistory.__dict__['__init__'](self)
        DocComments.__dict__['__init__'](self)


    ###########################
    #         ZMI FORMS       #
    ###########################

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/DocURL/url_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', abstract='', language='', coverage='', keywords='', sortorder='', approved='', locator='', REQUEST=None, **kwargs):
        """ updates URL instance properties """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = 100
        if approved: approved = 1
        else: approved = 0
        self.title = title
        self.description = description
        self.abstract = abstract
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.approved = approved
        self.locator = locator
        self.createHistory(HISTORY_EDIT)
        self._p_changed = 1
        self.recatalogDMObject(self)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')


    ######################
    #    SITE FORMS      #
    ######################

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'index_html')
    index_html = PageTemplateFile('zpt/DocURL/url_index', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/DocURL/url_edit', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'history_html')
    history_html = PageTemplateFile('zpt/DocURL/url_history', globals())

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'comments_html')
    comments_html = PageTemplateFile('zpt/DocURL/url_comments', globals())

    security.declareProtected(PERMISSION_EDIT_DMOBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', abstract='', language='', coverage='', keywords='', sortorder='', locator='', REQUEST=None, **kwargs):
        """ updates DocURL instance properties """
        if not self.checkPermissionEditObjects():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = 100
        self.title = title
        self.description = description
        self.language = language
        self.coverage = coverage
        self.keywords = keywords
        self.sortorder = sortorder
        self.locator = locator
        self.createHistory(HISTORY_EDIT)
        self._p_changed = 1
        self.recatalogDMObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('edit_html?dm_save=ok')

    security.declareProtected(PERMISSION_VIEW_DMOBJECTS, 'saveComment')
    def saveComment(self, doc_title='', doc_comment='', doc_email='', REQUEST=None):
        """ creates a comment """
        l_message = 'dm_save=err&doc_title=%s&doc_comment=%s&doc_email=%s' % (doc_title, doc_comment, doc_email)
        if self.utStrAllNotEmpty(doc_title, doc_comment, doc_email) and (self.utIsEmailValid(doc_email) or len(doc_email)==0):
            self.createComment(doc_title, doc_comment, doc_email)
            self.createHistory(HISTORY_COMMENT)
            l_message = 'dm_save=ok'
        if REQUEST: REQUEST.RESPONSE.redirect('comments_html?%s' % l_message)


    #############################
    #   Export in xml format    #
    #############################

    security.declarePrivate('exportThisCustomProperties')
    def exportThisCustomProperties(self):
        """ exports custom properties """
        return 'locator="%s"' % self.utXmlEncode(self.locator)


    #####################
    #   Syndication     #
    #####################

    security.declarePrivate('syndicateThis')
    def syndicateThis(self):
        """ syndicate informations """
        l_rdf = []
        l_rdf.append(self.syndicateThisHeader())
        l_rdf.append(self.syndicateThisCommon())
        l_rdf.append('<dc:type>Text</dc:type>')
        l_rdf.append('<dc:format>text</dc:format>')
        l_rdf.append('<dc:source>%s</dc:source>' % self.utXmlEncode(''))
        l_rdf.append(self.syndicateThisFooter())
        return ''.join(l_rdf)

InitializeClass(DocURL)