# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass
from OFS.Image import File, cookId
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.Naaya.constants import DEFAULT_SORTORDER
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from naaya.content.exfile import NyExFile
from naaya.content.exfile.exfile_item import addNyExFile

def addSurveyAttachment(container, id='', title='', description='', coverage='', keywords='', sortorder='',
    source='file', file='', url='', precondition='', content_type='', downloadfilename='',
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """ """
    if source=='file': id = cookId(id, title, file)[0] #upload from a file
    id = container.utCleanupId(id)
    if id == '': id = 'attachment_' + container.utGenRandomId(6)
    if downloadfilename == '': downloadfilename = id
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER

    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]

    #process parameters
    if contributor is None: contributor = container.REQUEST.AUTHENTICATED_USER.getUserName()
    if container.glCheckPermissionPublishObjects():
        approved, approved_by = 1, container.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = container.process_releasedate(releasedate)
    if lang is None: lang = container.gl_get_selected_language()
    #check if the id is invalid (it is already in use)
    i = 0
    while container._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    #create object
    ob = SurveyAttachment(id, contributor)
    container._setObject(ob.getId(), ob)
    ob = container._getOb(id)
    ob.saveProperties(title=title, description=description, coverage=coverage, keywords=keywords,
                      sortorder=sortorder, precondition=precondition, content_type=content_type,
                      downloadfilename=downloadfilename, releasedate=releasedate, lang=lang)
    container.gl_add_languages(ob)
    #ob.createDynamicProperties(container.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang) # ???
    #extra settings
    ob.updatePropertiesFromGlossary(lang)
    ob.submitThis()
    ob.approveThis(approved, approved_by)
    ob.handleUpload(source, file, url, lang)
    ob.createversion(container.REQUEST.AUTHENTICATED_USER.getUserName(), lang)
    if discussion: ob.open_for_comments()
    container.recatalogNyObject(ob)
    #log post date
    auth_tool = container.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        if l_referer == 'exfile_manage_add' or l_referer.find('exfile_manage_add') != -1:
            return container.manage_main(container, REQUEST, update_menu=1)
        elif l_referer == 'attachment_add':
            container.setSession('referer', container.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % container.absolute_url())

# it should be the other way arround; NyExFile should inherit from SurveyAttachment
class SurveyAttachment(NyExFile):
    """NyExFile with reduced (crippled) functionality"""

    meta_type = "Naaya Survey Attachment"
    meta_label = "Attachment"

    _constructors = (addSurveyAttachment, )

    security = ClassSecurityInfo()

    def _get_schema(self):
        meta_type = super(NyExFile, self).meta_type
        return self.getSite().getSchemaTool().getSchemaForMetatype(meta_type)

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/attachment_index', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/attachment_edit', globals())

InitializeClass(SurveyAttachment)
