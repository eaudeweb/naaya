import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase


ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
ZopeTestCase.installProduct('NaayaCore')
ZopeTestCase.installProduct('NaayaContent')
ZopeTestCase.installProduct('NaayaBase')
ZopeTestCase.installProduct('naayaHotfix')
ZopeTestCase.installProduct('Naaya')
ZopeTestCase.installProduct('iHotfix')
ZopeTestCase.installProduct('PythonScripts', quiet=1)

from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, noSecurityManager

from Products.Naaya.NySite import NySite, manage_addNySite
from Products.NaayaContent.NyNews.NyNews import addNyNews
from Products.NaayaContent.NyDocument.NyDocument import addNyDocument
from Products.NaayaContent.NyEvent.NyEvent import addNyEvent
from Products.NaayaContent.NyBlogEntry.NyBlogEntry import addNyBlogEntry
from Products.NaayaContent.NyExFile.NyExFile import addNyExFile
from Products.NaayaContent.NyFile.NyFile import addNyFile
from Products.NaayaContent.NyMediaFile.NyMediaFile import addNyMediaFile
from Products.NaayaContent.NyPointer.NyPointer import addNyPointer
from Products.NaayaContent.NyURL.NyURL import addNyURL
from Products.NaayaContent.NyStory.NyStory import addNyStory
from Products.Naaya.NyFolder import addNyFolder


# Open ZODB connection
app = ZopeTestCase.app()

# Close ZODB connection
ZopeTestCase.close(app)

#-------------------------------------------------------------------------------
# The folowing are patches needed because Localizer doesn't work
# well within ZTC
# This one is needed by ProxyTool.
def get_selected_language(self):
    """ """
    return 'en'

from Products.Localizer.Localizer import LanguageManager
LanguageManager.get_selected_language = get_selected_language

# Dummy portal_catalog.
from OFS.SimpleItem import SimpleItem
class DummyTranslationService(SimpleItem):
    meta_type = 'Translation Service'
    id = 'translation_service'
    def translate(self, domain, msgid, *args, **kw):
        return msgid

    def getDomainInfo(self):
        return [(None, 'Localizer/default')]

    def manage_addDomainInfo(self, domain, path, REQUEST=None, **kw):
        pass

# Dummy MessageCatalog
class DummyMessageCatalog:
    def __call__(self, message, *args, **kw):
        return message

    def get_selected_language(self):
        "xxx"
        return 'en'

    def get_languages(self):
        return ['en', 'fr']

    def manage_import(self, *args, **kw):
        pass

    def wl_isLocked(self):
        return None # = False

# Change translation_service to DummyTranslationService
def fixupTranslationServices(root, portal):
    portal.translation_service = DummyTranslationService()
    localizer = portal.portal_translations
    for domain in localizer.objectIds():
        setattr(localizer, domain, DummyMessageCatalog())
#-------------------------------------------------------------------------------

class NaayaTests(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        """ add a Naaya portal and create a Naaya Folder """
        self.root = app  #get Zope ROOT
        #create a default user in the users folder
        self.root.acl_users.userFolderAddUser("admin", "admin", ["Manager"], [])
        user = self.root.acl_users.getUserById('admin').__of__(self.root.acl_users)
        newSecurityManager(None, user)
        #add REQUEST variabiles
        self.root.REQUEST.AUTHENTICATED_USER = self.root.acl_users.getUser('admin')
        #add Naaya portal and patch the Localizer
        manage_addNySite(self.root, id='naaya-test', title='Naaya test site', default_content=True)
        self.portal = self.root._getOb('naaya-test')
        fixupTranslationServices(self.root, self.portal)
        
        #create NyFolder
        addNyFolder(self.portal, title='test_folder', id='folder_test', lang='en')

    def testChangeSiteTitle(self):
        lang = self.portal.gl_get_selected_language()
        self.portal._setLocalPropValue('title', lang, 'portal_title')
        self.portal._setLocalPropValue('site_title', lang, 'site_title')
        self.portal._setLocalPropValue('title', 'fr', 'portal_title_fr')
        self.portal._setLocalPropValue('site_title', 'fr', 'site_title_fr')
        self.portal._p_changed = 1
        self.assertEqual(self.portal.getLocalProperty('title', lang), 'portal_title')
        self.assertEqual(self.portal.getLocalProperty('title', 'fr'), 'portal_title_fr')

    def testChangeEmailServer(self):
        new_server = 'newMailServer'
        self.portal.getEmailTool().manageSettings(mail_server_name=new_server)
        self.assertEqual(self.portal.mail_server_name, new_server)

    def test_NyNews(self):
        """ Add, Find, Edit and Delete Naaya News """
        #add Naaya News
        addNyNews(self.portal.folder_test, title='news1', lang='en')
        addNyNews(self.portal.folder_test, title='news1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya News'])
        
        #Get added NyNews
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'news1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'news1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'news1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'news1_fr')
        
        #Change NyNews title
        meta.saveProperties(title='news1_edited', lang='en')
        meta_fr.saveProperties(title='news1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'news1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'news1_fr_edited')
        
        #delete NyNews
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya News'])
        
        self.assertEqual(meta, [])


    def test_NyDocument(self):
        """ Add, Find, Edit and Delete Naaya Documents """
        #add NyDocument
        addNyDocument(self.portal.folder_test, id='doc1', title='doc1', lang='en', submitted=1)
        addNyDocument(self.portal.folder_test, id='doc1_fr', title='doc1_fr', lang='fr', submitted=1)
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Document'])
        
        #Get added NyDocument
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'doc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'doc1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr')
        
        #Change NyDocument title
        meta.saveProperties(title='doc1_edited', lang='en')
        meta_fr.saveProperties(title='doc1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr_edited')
        
        #delete NyDocument
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Document'])
        for x in meta:
            if x.id == 'doc1':
                meta = x
            else:
                meta = []
            
            if x.id == 'doc1_fr':
                meta_fr = x
            else:
                meta_fr = []
            
        self.assertEqual(meta, [])
        self.assertEqual(meta_fr, [])


    def test_NyEvent(self):
        """ Add, Find, Edit and Delete Naaya Events """
        #add NyEvent
        addNyEvent(self.portal.folder_test, id='event1', title='event1', lang='en')
        addNyEvent(self.portal.folder_test, id='event1_fr', title='event1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Event'])
        
        #get added NyEvent
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'event1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'event1_fr':
                meta_fr = x
            
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'event1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'event1_fr')
        
        #change NyEvent title
        meta.saveProperties(title='event1_edited', lang='en')
        meta_fr.saveProperties(title='event1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'event1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'event1_fr_edited')
        
        #delete NyEvent
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Event'])
        self.assertEqual(meta, [])


    def test_NyBlogEntry(self):
        """ Add, Find, Edit and Delete Naaya Blog Entries """
        #add NyBlog
        addNyBlogEntry(self.portal.folder_test, id='blog1', title='blog1', lang='en', submitted=1)
        addNyBlogEntry(self.portal.folder_test, id='blog1_fr', title='blog1_fr', lang='fr', submitted=1)
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Blog Entry'])
        
        #get added NyBlog
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'blog1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'blog1_fr':
                meta_fr = x
                
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'blog1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'blog1_fr')
        
        #change NyBlog title
        meta.saveProperties(title='blog1_edited', lang='en')
        meta_fr.saveProperties(title='blog1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'blog1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'blog1_fr_edited')
        
        #delete NyBlog
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Blog Entry'])
        self.assertEqual(meta, [])


    def test_NyExFile(self):
        """ Add, Find, Edit and Delete Naaya Extended Files """
        #add NyExFile
        addNyExFile(self.portal.folder_test, id='exfile1', title='exfile1', lang='en')
        addNyExFile(self.portal.folder_test, id='exfile1_fr', title='exfile1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Extended File'])
        #get added NyExFile
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'exfile1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'exfile1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'exfile1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'exfile1_fr')
        
        #change NyExFile title
        meta.saveProperties(title='exfile1_edited', lang='en')
        meta_fr.saveProperties(title='exfile1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'exfile1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'exfile1_fr_edited')
        
        #delete NyExFile
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Extended File'])
        self.assertEqual(meta, [])


    def test_NyFile(self):
        """ Add, Find, Edit and Delete Naaya Files """
        #add NyFile
        addNyFile(self.portal.folder_test, id='file1', title='file1', lang='en')
        addNyFile(self.portal.folder_test, id='file1_fr', title='file1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya File'])
        
        #get added NyFile
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'file1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'file1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'file1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'file1_fr')
        
        #change NyFile title
        meta.saveProperties(title='file1_edited', lang='en')
        meta_fr.saveProperties(title='file1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'file1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'file1_fr_edited')
        
        #delete NyFile
        self.portal.folder_test.manage_delObjects([meta.getId()])
        self.portal.folder_test.manage_delObjects([meta_fr.getId()])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya File'])
        self.assertEqual(meta, [])

    def test_NyMediaFile(self):
        """ Add, Find, Edit and Delete Naaya Media Files """
        #add NyMediaFile
        addNyMediaFile(self.portal.folder_test, id='media1', title='media1', lang='en')
        addNyMediaFile(self.portal.folder_test, id='media1_fr', title='media1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])
        
        #get added NyMediaFile
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'media1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'media1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'media1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'media1_fr')
        
        #change NyMediaFile title
        meta.saveProperties(title='media1_edited', lang='en')
        meta_fr.saveProperties(title='media1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'media1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'media1_fr_edited')
        
        #delete NyMediafile
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Media File'])
        self.assertEqual(meta, [])

    def test_NyPointer(self):
        """ Add, Find, Edit and Delete Naaya Pointers """
        #add NyPointer
        addNyPointer(self.portal.folder_test, id='pointer1', title='pointer1', lang='en')
        addNyPointer(self.portal.folder_test, id='pointer1_fr', title='pointer1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])
        
        #get added NyPointer
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'pointer1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'pointer1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pointer1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pointer1_fr')
        
        #change NyPointer title
        meta.saveProperties(title='pointer1_edited', lang='en')
        meta_fr.saveProperties(title='pointer1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pointer1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pointer1_fr_edited')
        
        #delete NyPointer
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])
        self.assertEqual(meta, [])


    def test_NyURL(self):
        """ Add, Find, Edit and Delete Naaya URLs """
        #add NyURL
        addNyURL(self.portal.folder_test, id='url1', title='url1', lang='en')
        addNyURL(self.portal.folder_test, id='url1_fr', title='url1_fr', lang='fr')
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya URL'])
        
        #get added NyURL
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'url1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'url1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'url1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'url1_fr')
        
        #change NyURL title
        meta.saveProperties(title='url1_edited', lang='en')
        meta_fr.saveProperties(title='url1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'url1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'url1_fr_edited')
        
        #delete NyURL
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya URL'])
        self.assertEqual(meta, [])


    def test_NyStory(self):
        """ Add, Find, Edit and Delete Naaya Stories """
        #add NyStory
        addNyStory(self.portal.folder_test, id='story1', title='story1', lang='en', submitted=1)
        addNyStory(self.portal.folder_test, id='story1_fr', title='story1_fr', lang='fr', submitted=1)
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Story'])
        
        #get added NyStory
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'story1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'story1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'story1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'story1_fr')
        
        #change NyStory title
        meta.saveProperties(title='story1_edited', lang='en')
        meta_fr.saveProperties(title='story1_fr_edited', lang='fr')
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'story1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'story1_fr_edited')
        
        #delete NyStory
        self.portal.folder_test.manage_delObjects([meta.id])
        self.portal.folder_test.manage_delObjects([meta_fr.id])
        
        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Story'])
        self.assertEqual(meta, [])

    def test_userManagement(self):
        """ Add, Find, Edit and Delete a User"""
        usr_name = 'test_user'
        usr_pwd = 'test_user_password'
        usr_mail = 'test_user_email'
        
        #Add user.
        self.portal.getAuthenticationTool().manage_addUser(name=usr_name, password=usr_pwd, confirm=usr_pwd, firstname=usr_name, lastname=usr_name, email=usr_mail)
        
        #get user object
        usr_obj = self.portal.getAuthenticationTool().getUser('test_user')
        self.assertEqual(usr_obj.name, 'test_user')
        
        #change user email
        self.portal.getAuthenticationTool().manage_changeUser(name=usr_name, password=usr_pwd, confirm=usr_pwd, 
                                                              email='changed_test_user_email', firstname=usr_name, lastname=usr_name)
        self.assertEqual(usr_obj.email, 'changed_test_user_email')
        
        #add user roles
        self.portal.getAuthenticationTool().manage_addUsersRoles(name=usr_obj.name, roles=['Administrator', 'Manager', 'Contributor'])
        self.assertEqual(usr_obj.roles, ['Administrator', 'Manager', 'Contributor'])
        
        #revoke user roles
        self.portal.getAuthenticationTool().manage_revokeUsersRoles('%s||' % usr_obj.name)
        self.assertEqual(usr_obj.roles, [])
        
        #delete user
        self.portal.getAuthenticationTool().manage_delUsers(names=[usr_obj.name])
        self.assertEqual(self.portal.getAuthenticationTool().getUser('test_user'), None)

    def test_roles(self):
        """ Add, Edit and Delete a Role """
        new_role = 'Test Role'
        permissions = ['Add content', 'Edit content']
        permission = ['Edit content']
        initial_roles = self.portal.getAuthenticationTool().list_all_roles()
        modified_roles = initial_roles[:]
        modified_roles.append(new_role)
        
        #add Role
        test_role = self.portal.getAuthenticationTool().addRole(new_role)
        get_permissions = self.portal.getAuthenticationTool().getRolePermissions(new_role)
        list_roles = self.portal.getAuthenticationTool().list_all_roles()
        self.assertEqual(get_permissions, [])
        self.assertEqual(list_roles, modified_roles)
        
        #add Permisions to role
        edit_permissions = self.portal.getAuthenticationTool().editRole(new_role, permissions)
        get_permissions = self.portal.getAuthenticationTool().getRolePermissions(new_role)
        self.assertEqual(get_permissions, permissions)
        
        #remove permission from role
        edit_permissions = self.portal.getAuthenticationTool().editRole(new_role, permission)
        get_permissions = self.portal.getAuthenticationTool().getRolePermissions(new_role)
        self.assertEqual(get_permissions, permission)
        
        #remove all permissions from role
        edit_permissions = self.portal.getAuthenticationTool().editRole(new_role)
        get_permissions = self.portal.getAuthenticationTool().getRolePermissions(new_role)
        self.assertEqual(get_permissions, [])
        
        #delete role
        self.portal.getAuthenticationTool().delRole(new_role)
        list_roles = self.portal.getAuthenticationTool().list_all_roles()
        self.assertEqual(list_roles, initial_roles)

    def beforeTearDown(self):
        """ delete the test portal """
        noSecurityManager()
        self.root.manage_delObjects(self.portal.id)

if __name__ == '__main__':
    framework()