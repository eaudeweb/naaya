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

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from RemoteChannel import RemoteChannel

manage_addRemoteChannelFacadeForm = PageTemplateFile('zpt/remotechannelfacade_manage_add', globals())
def manage_addRemoteChannelFacade(self, id='', title='', url='', providername='',
    location='', obtype='news', numbershownitems='', portlet='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_SUFIX_REMOTECHANNELFACADE % self.utGenRandomId(6)
    try: numbershownitems = abs(int(numbershownitems))
    except: numbershownitems = 0
    ob = RemoteChannelFacade(id, title, url, providername, location, obtype, numbershownitems)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_remotechannelfacade(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class RemoteChannelFacade(RemoteChannel):
    """ """

    meta_type = METATYPE_REMOTECHANNELFACADE
    icon = 'misc_/NaayaCore/RemoteChannelFacade.gif'

    manage_options = (
        RemoteChannel.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, url, providername, location, obtype, numbershownitems):
        """ """
        RemoteChannel.__dict__['__init__'](self, id, title, url, numbershownitems)
        self.providername = providername
        self.location = location
        self.obtype = obtype

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        RemoteChannelFacade.inheritedAttribute('manage_beforeDelete')(self, item, container)

    #api
    def generateContent(self):
        """
        Generates object in channel's defined location. The objects are by default
        unapproved.
        """
        location_ob = self.utGetObject(self.location)
        if location_ob:
            #start create objects from RDF items
            if self.obtype == 'news':
                #create news objects
                for feed_item in self.get_feed_items():
                    id = self.utToUtf8(feed_item.id.split('/')[-1])
                    tags = [x['term'] for x in feed_item.tags]
                    keywords = [x.strip() for x in feed_item.ut_keywords.split(',')]
                    subject = self.utListDifference(tags, feed_item.ut_keywords)
                    location_ob.addNySemNews(id=id,
                        creator=feed_item.author,
                        creator_email=feed_item.ut_creator_mail,
                        contact_person=feed_item.ut_contact_name,
                        contact_email=feed_item.ut_contact_mail,
                        contact_phone=feed_item.ut_contact_phone,
                        rights=feed_item.rights,
                        title=feed_item.title_detail['value'],
                        news_type=feed_item.ut_news_type,
                        file_link=feed_item.ut_file_link,
                        file_link_local=feed_item.ut_file_link_local,
                        source=feed_item.dc_source,
                        source_link=feed_item.ut_source_link,
                        keywords=feed_item.ut_keywords,
                        description=feed_item.dc_description,
                        subject=subject,
                        relation=feed_item.dc_relation,
                        coverage=feed_item.dc_coverage,
                        news_date=self.utConvertDateTimeHTMLToString(feed_item.ut_start_date),
                        lang=feed_item.language)
                    ob = location_ob._getOb(id)
                    ob.approveThis(0, None)
        else:
            pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', url='', providername='', location='',
        obtype='news', numbershownitems='', REQUEST=None):
        """ """
        try: numbershownitems = abs(int(numbershownitems))
        except: numbershownitems = self.numbershownitems
        self.title = title
        self.url = url
        self.providername = providername
        self.location = location
        self.obtype = obtype
        self.numbershownitems = numbershownitems
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    #zmi forms
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/remotechannelfacade_properties', globals())

InitializeClass(RemoteChannelFacade)
