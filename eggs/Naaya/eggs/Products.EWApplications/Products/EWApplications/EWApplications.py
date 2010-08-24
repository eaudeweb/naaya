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
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
#
#
#
#$Id: EWApplications.py 2705 2004-11-26 14:30:23Z finrocvs $

#Python imports
import xmlrpclib
import rotor
from os.path import join

#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

#Product imports
from constants import *
from Products.EWPublisher.constants import PERMISSION_PUBLISH_EWOBJECTS, EWPUBLISHER_PRODUCT_PATH
from Products.EWInstaller.constants import EWINSTALLER_ID
from Products.EWPublisher.EWCore.UtilsTool.utils import utils, file_utils
import EWApplication
from BasicAuthTransport import BasicAuthTransport

manage_addEWApplications_html = PageTemplateFile('zpt/applications_manage_add', globals())
manage_addEWApplications_html.EWKind = METATYPE_EWAPPLICATIONS
manage_addEWApplications_html.EWAction = 'addEWApplications'

def addEWApplications(self, id='', title='', description='', email_subject='', email_from='', email_to='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_EWAPPLICATIONS + self.utGenRandomId(6)
    ob = EWApplications(id, title, description, email_subject, email_from, email_to)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class EWApplications(Folder,
    utils,
    file_utils):
    """ EWApplications class """

    meta_type = METATYPE_EWAPPLICATIONS

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label' : 'Properties', 'action' : 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_EWAPPLICATION, 'action': 'manage_addEWApplication_html'},
    )
    all_meta_types = meta_types

    manage_addEWApplication_html = EWApplication.manage_addEWApplication_html

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, email_subject, email_from, email_to):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.email_subject = email_subject
        self.email_from = email_from
        self.email_to = email_to
        utils.__dict__['__init__'](self)
        file_utils.__dict__['__init__'](self)

    def __setstate__(self, state):
        """ """
        EWApplications.inheritedAttribute('__setstate__')(self, state)

    def __generateZopePageTemplate(self, p_folder, p_id, p_title, p_content):
        #add a ZopePageTemplate object
        manage_addPageTemplate(p_folder, id=p_id, title=p_title, text='')
        p_folder._getOb(p_id).pt_edit(text=p_content, content_type='')

    def __getContent(self, p_context={}, p_page=None):
        #Render interface pages
        return self._getOb(p_page).pt_render(extra_context=p_context)

    security.declareProtected('Add EWApplications object', 'loadDefaultData')
    def loadDefaultData(self):
        #loads all the wizard pages into Zope as PageTemplate objects
        self.__generateZopePageTemplate(self, 'applications_index', 'Start page', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_index.zpt')))
        self.__generateZopePageTemplate(self, 'applications_step1', 'Step 1', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_step1.zpt')))
        self.__generateZopePageTemplate(self, 'applications_step2', 'Step 2', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_step2.zpt')))
        self.__generateZopePageTemplate(self, 'applications_step3', 'Step 3', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_step3.zpt')))
        self.__generateZopePageTemplate(self, 'applications_step4', 'Step 4', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_step4.zpt')))
        self.__generateZopePageTemplate(self, 'applications_step5', 'Step 5', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_step5.zpt')))
        self.__generateZopePageTemplate(self, 'applications_confirm', 'Confirm', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_confirm.zpt')))
        self.__generateZopePageTemplate(self, 'applications_finish', 'Finish', self.futRead(join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 'applications_finish.zpt')))

    #Wizard methods
    def getEmptyApplicationData(self):
        return {
            'site_title':'', 'subtitle':'', 'description':'', 'publisher':'', 'contributor':'', 'language':'','creator':'', 'rights':'', 'agreed':'checked','warning':'',
            'contact_name':'', 'contact_email':'', 'administrator_name':'', 'administrator_email':'', 'username':'', 'password':'', 'portal_url':'',
            'featured': 'Yes', 'topic': '','category':'',
            'products':[], 'main_topic_a_title':'', 'main_topic_b_title':'', 'main_topic_c_title':'', 'main_topic_d_title':'',
            'site_icon':None,
            'skin':'eionet', 'colourscheme':'orange'
        }

    def getEWLogo(self):
        """."""
        file = open(join(EWPUBLISHER_PRODUCT_PATH, 'EWContent', 'images', 'EWLogo.gif'), 'rb')
        content = file.read()
        file.close()
        return content

    def setMyPicture(self, p_picture):
        """ """
        self.logo_icon = None
        if p_picture:
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.logo_icon = l_read
                        self._p_changed = 1
            else:
                self.logo_icon = p_picture
                if self.logo_icon is not None:
                    print 'is not none'
                self._p_changed = 1
                return self.logo_icon

    def applicationInit(self):
        self.REQUEST.SESSION.set(APPLICATION_DATA, self.getEmptyApplicationData())

    def step1_process(self, site_title='', subtitle='', description='', publisher='', contributor='', creator='', rights='', language='', agreed='', REQUEST=None):
        """ """
        application_data = REQUEST.SESSION.get(APPLICATION_DATA, self.getEmptyApplicationData())
        application_data['site_title'] = site_title
        application_data['subtitle'] = subtitle
        application_data['description'] = description
        application_data['publisher'] = publisher
        application_data['contributor'] = contributor
        application_data['creator'] = creator
        application_data['rights'] = rights
        application_data['language'] = language
        if not agreed:
            application_data['warning'] = 'You must agree to the Terms of Service'
            REQUEST.SESSION.set(APPLICATION_DATA, application_data)
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/step1_html')
        else:
            REQUEST.SESSION.set(APPLICATION_DATA, application_data)
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/step2_html')

    def step2_process(self, contact_name='', contact_email='', administrator_name='', administrator_email='', username='', password='', portal_url='', REQUEST=None):
        """ """
        application_data = REQUEST.SESSION.get(APPLICATION_DATA, self.getEmptyApplicationData())
        application_data['contact_name'] = contact_name
        application_data['contact_email'] = contact_email
        application_data['administrator_name'] = administrator_name
        application_data['administrator_email'] = administrator_email
        application_data['portal_url'] = portal_url
        application_data['username'] = username
        application_data['password'] = password
        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/step3_html')

    def step3_process(self, featured='Yes', topic='', category=None, REQUEST=None):
        """ """
        application_data = REQUEST.SESSION.get(APPLICATION_DATA, self.getEmptyApplicationData())
        application_data['featured'] = featured
        if category is None:
            category =''
            category_url=''
        else:
            buf = category.split('||')
            category = buf[1]
            category_url = buf[0]

        if featured == 'Yes':
            application_data['topic'] = topic
            application_data['category'] = category
            application_data['category_url'] = category_url
        else:
            application_data['topic'] = ''
            application_data['category']=''
            application_data['category_url']=''

        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/step4_html')

    def step4_process(self, products=None, REQUEST=None):
        """ """
        if products is None: products = []
        else:
            try:
                products.reverse()
            except:
                products = [products]
        application_data = REQUEST.SESSION.get(APPLICATION_DATA, self.getEmptyApplicationData())
        application_data['products'] = products
        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/step5_html')

    def step5_process(self, skin='eionet', eionet_colourscheme='orange', autumn_colourscheme='brown', metal_colourscheme='blue', site_icon=None, main_topic_a_title='', main_topic_b_title='', main_topic_c_title='', main_topic_d_title='', REQUEST=None):
        """ """
        application_data = REQUEST.SESSION.get(APPLICATION_DATA, self.getEmptyApplicationData())
        application_data['main_topic_a_title'] = main_topic_a_title
        application_data['main_topic_b_title'] = main_topic_b_title
        application_data['main_topic_c_title'] = main_topic_c_title
        application_data['main_topic_d_title'] = main_topic_d_title
        a = site_icon.read()
        if a == '':
            application_data['site_icon'] = self.getEWLogo()
        else:
            application_data['site_icon'] = a

        application_data['skin'] = skin
        if skin == 'eionet':
            application_data['colourscheme'] = eionet_colourscheme
        elif skin == 'autumn':
            application_data['colourscheme'] = autumn_colourscheme
        elif skin == 'metal':
            application_data['colourscheme'] = metal_colourscheme
        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/confirm_html')

    def confirm_process(self, REQUEST):
        """ """
        application_data = REQUEST.SESSION.get(APPLICATION_DATA, self.getEmptyApplicationData())
        #create application object
        id = PREFIX_EWAPPLICATION + self.utGenRandomId(6)
        ob = EWApplication.EWApplication(id, application_data['site_title'], application_data['site_icon'], application_data, '', self.utGetTodayDate())
        self._setObject(id, ob)
        #send notification email
        l_category = application_data['category']
        l_topic = application_data['topic']
        if l_category == '':
            l_category = 'N/A'
            l_topic = 'N/A'
        l_products = ', '.join(application_data['products'])
        if l_products == '': l_products = 'None'

        l_subject = self.email_subject
        l_from = self.email_from
        l_to = self.email_to
        l_content = """
An application for the creation of an EnviroWindows-compliant portal has been made
with the following information:

Portal title:             %s
Portal subtitle:          %s
Description:              %s
Publisher                 %s
Contributor:              %s
Creator:                  %s
Rights:                   %s
Language:                 %s

Contact person:           %s
Contact email:            %s
Administrator name:       %s
Administrator email:      %s
Portal URL:               %s

Is this an EW Featured Partner Site:    %s
    EnviroWindows category              %s
    EnviroWindows related topic         %s

Additional functionality: %s

Skin:                     %s
Color scheme:             %s

You can review this application and decide to create the portal or reject it
from the applications' basket in the EnviroWindows website.
""" % (
        application_data['site_title'],
        application_data['subtitle'],
        application_data['description'],
        application_data['publisher'],
        application_data['contributor'],
        application_data['creator'],
        application_data['rights'],
        application_data['language'],
        application_data['contact_name'],
        application_data['contact_email'],
        application_data['administrator_name'],
        application_data['administrator_email'],
        application_data['portal_url'],
        application_data['featured'],
        l_category,
        l_topic,
        l_products,
        application_data['skin'],
        application_data['colourscheme'])
        self.getEWSite().getEmailTool().sendGenericEmail(l_content, l_to, l_from, l_subject)
        try:
            REQUEST.SESSION.delete(APPLICATION_DATA)
        except:
            pass            
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/finish_html')

    # API
    def getApplicationsContainer(self):
        #returns this object
        return self

    def getApplications(self):
        #returns all applications
        return self.objectValues(METATYPE_EWAPPLICATION)

    def getEWInstaller(self):
        #return the root's object EWInstaller
        return self.unrestrictedTraverse(EWINSTALLER_ID, None)

    def __valideIssueProperty(self, param):
        """Check if exists a property with given value"""
        return param in ['request_date', 'status', 'title']

    def __validParams(self, sortby, how):
        """Validate sort parameters"""
        res = 1
        if (how != 'asc' and how != 'desc'):
            res = 0
        else:
            if (self.__valideIssueProperty(sortby)):
                res = 1
            else:
                res = 0
        return res

    def getApplicationsSorted(self, sortby, how):
        """returns all applications sorted by an attribute"""
        l_apps = self.getApplications()
        if self.__validParams(sortby, how):
            if how == 'asc': how = 0
            else: how = 1
            l_apps = self.utSortObjsListByAttr(l_apps, sortby, how)
        return l_apps

    def getEWCategories(self):
        """get EW categories, using the /methods/get_fps python script"""
        try: return self.getEWSite().methods.get_fps()
        except: return []

    def getConstant(self, constant=''):
        """gets the value from a constant from constants.py; used mainly for status_messages"""
        return eval(constant)

    # ZMI FORMS
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/applications_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', email_subject='', email_from='', email_to='', REQUEST=None):
        """Update EWApplications instance properties"""
        self.title = title
        self.description = description
        self.email_subject = email_subject
        self.email_from = email_from
        self.email_to = email_to
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    # SITE FORMS
    security.declareProtected(view, 'index_html')
    def index_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_index')

    security.declareProtected(view, 'step1_html')
    def step1_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step1')

    security.declareProtected(view, 'step2_html')
    def step2_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step2')

    security.declareProtected(view, 'step3_html')
    def step3_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step3')

    security.declareProtected(view, 'step4_html')
    def step4_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step4')

    security.declareProtected(view, 'step5_html')
    def step5_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step5')

    security.declareProtected(view, 'confirm_html')
    def confirm_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_confirm')

    security.declareProtected(view, 'finish_html')
    def finish_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_finish')

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'basket_html')
    basket_html = PageTemplateFile('zpt/applications_basket', globals())

InitializeClass(EWApplications)
