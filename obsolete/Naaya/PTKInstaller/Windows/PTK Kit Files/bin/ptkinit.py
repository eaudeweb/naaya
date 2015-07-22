# This script will create default Naaya site

#Python imports
import os
import sys
import popen2
import time
import msvcrt
from os import environ
from sys import stdin, stdout

#Zope imports
import Zope
import ZODB
import Globals
import App.Product
from AccessControl.SecurityManagement import newSecurityManager
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.BaseRequest import RequestContainer

#Naaya tool imports
from Products.Naaya.NySite import NySite, manage_addNySite

class make_fake_user:

    def getUserName(self):
        return '@@USERNAME@@'

class PortalInit:

    def __init__(self, registerservices):
        #memeber variables
        self.registerservices = registerservices
        self.root = None
        self.r, self.w, self.e = None, None, None

    def exit_script(self, error):
        #exit script when an error occured
        print error
        print 'Configuration script stoped.\n'
        print 'Press any key to continue...'
        msvcrt.getch()
        sys.exit(1)

    def connect_to_zodb(self):
        #connect to ZODB
        try:
            print '\tConnect to ZODB...\n'
            Zope.configure(os.environ['CONFIG_FILE'])
            self.root = Zope.app()
            self.root = self.makerequest()
            self.login_to_zodb()
        except Exception, error:
            #failed to connect to ZODB
            self.exit_script('\tFailed to connect to ZODB: %s.\n' % str(error))
        else:
            print '\t\tDone.\n'

    def login_to_zodb(self):
        acl = self.root.acl_users
        user = acl.getUserById('@@USERNAME@@')
        assert user is not None
        user = user.__of__(acl)
        newSecurityManager(None, user)

    def makerequest(self, stdout=stdout):
        # copy/hacked from Testing.makerequest
        resp = HTTPResponse(stdout=stdout)
        environ['SERVER_NAME']='@@HOSTNAME@@'
        environ['SERVER_PORT']='@@ZOPE_PORT@@'
        environ['REQUEST_METHOD'] = 'GET'
        req = HTTPRequest(stdin, environ, resp)

        # first put the needed values in the request
        req['HTTP_ACCEPT_CHARSET'] = 'utf-8'
        req['HTTP_ACCEPT_LANGUAGE'] = 'en'
        req['AUTHENTICATED_USER'] = make_fake_user()

        # ok, let's wrap and return
        return self.root.__of__(RequestContainer(REQUEST = req))

    def commit_changes_in_zodb(self):
        #commit changes and disconnect form ZODB
        try:
            print '\tCommit changes in ZODB..\n'
            get_transaction().commit()
            self.root._p_jar.sync()
        except Exception, error:
            #failed to commit changes in ZODB
            self.exit_script('\tFailed to commit changes in ZODB: %s.\n' % str(error))
        else:
            print '\t\tDone.\n'

    def create_portal(self):
        #add a portal in ZODB
        try:
            print '\tCreating the portal object in ZODB...\n'
            self.root.manage_addProperty('management_page_charset', 'utf-8', 'string')
            add_error = manage_addNySite(self.root, id='portal', lang='en')
        except Exception, error:
            #failed to add the portal
            self.exit_script('\tFailed to add the portal object in ZODB: %s.\n' % str(error))
        else:
            if add_error is not None:
                self.exit_script('\tFailed to add the portal object in ZODB: %s.\n' % str(add_error))
            else:
                print '\tSetup the portal...\n'
                portal = self.root.portal
                try:
                    #metadata
                    portal.admin_metadata(site_title='@@PORTAL_TITLE@@',
                        site_subtitle='@@PORTAL_SUBTITLE@@',
                        publisher='@@PORTAL_PUBLISHER@@',
                        contributor='@@PORTAL_CONTRIBUTOR@@',
                        creator='@@PORTAL_CREATOR@@',
                        rights='@@PORTAL_RIGHTS@@', lang='en')
                    #administrative stuff
                    portal.getEmailTool().manageSettings(mail_server_name='@@PORTAL_MAILSERVERNAME@@',
                        mail_server_port='@@PORTAL_MAILSERVERPORT@@',
                        administrator_email='@@PORTAL_ADMINISTRATOREMAIL@@',
                        mail_address_from='@@PORTAL_DEFAULTFROMADDRESS@@', notify_on_errors='1')
                    for l in [@@PORTAL_LANGUAGES@@]:
                        portal.gl_add_site_language(l)
                    #main topics
                    portal.getPropertiesTool().manageMainTopics(maintopics=[])
                except Exception, error:
                    #failed to setup the portal
                    self.exit_script('\tFailed to setup the portal in ZODB: %s.\n' % str(error))
                else:
                    print '\t\tDone.\n'

    def register_services(self):
        #register services
        if self.registerservices:
            try:
                print '\tStart register services...\n'
                self.r, self.w, self.e = popen2.popen3(r'@@BIN_PATH@@\installservice.bat')
                print ''.join(self.r.readlines())
            except Exception, error:
                #failed to register services
                self.exit_script('\tFailed to register services: %s.\n' % str(error))
            else:
                print '\t\tDone.\n'

    def start(self):
        #start configuration
        print
        print 'Start configuration script'
        print '--------------------------'
        print
        #Zope stuff
        self.connect_to_zodb()
        self.create_portal()
        self.commit_changes_in_zodb()
        self.register_services()
        print
        print 'Stop configuration script'
        print '--------------------------'
        print
        print 'Press any key to continue...'
        msvcrt.getch()

if __name__ == '__main__':

    #parse arguments command line arguments
    registerservices = 0
    arguments = sys.argv[1:]
    if len(arguments) > 0:
        if arguments[0] == '--install':
            registerservices = 1

    #patch method
    def gl_get_selected_language(self): return 'en'
    NySite.gl_get_selected_language = gl_get_selected_language

    c2i = PortalInit(registerservices)
    c2i.start()

    #restore method
    def gl_get_selected_language(self): return self.get_selected_language()
    NySite.gl_get_selected_language = gl_get_selected_language
