# -*- coding: iso-8859-15 -*-
#################################################################################
#										#
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,		#
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez    		#
# Christian Martel								#
#										#
# This program is free software; you can redistribute it and/or			#
# modify it under the terms of the GNU General Public License			#
# as published by the Free Software Foundation; either version 2		#
# of the License, or (at your option) any later version.			#
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software      		#
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#										#
#################################################################################

__doc__ = """Zope Exist OAI Site Harvester"""

import string

from Globals import HTMLFile, Persistent
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
import App
import zOAIRecord # for manage_addOAIRecord
from pyOAIMH.OAIHarvester import OAIHarvester
from pyOAIMH.OAIHarvester import HTTPLibError, ServerError

from OFS.SimpleItem import Item

import random
from DateTime import DateTime

import zOAISupport  # for processId

manage_addOAIExistHarvesterForm = HTMLFile('dtml/manage_addOAIExistHarvesterForm', globals())

def manage_addOAIExistHarvester(self, host="", url="", title="", days=7, REQUEST=None, RESPONSE=None):
    """ method for adding a new Exist OAI object """
 
    if url == "":
        if RESPONSE is not None:
            RESPONSE.redirect(self.absolute_url()+'/manage_main?error_message=' + 'Vous%20devez%20choisir%20un%20url')
            return None

           
    try:
         id = zOAISupport.processId(host)
         OAIS = zOAIExistHarvester(id, host, url, title, days)
    except:
        import traceback
        traceback.print_exc()
        
    self._setObject(id, OAIS)
    OAIS = getattr(self, id)
    
    OAIS.initialize()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main?update_menu=1')




class zOAIExistHarvester(OAIHarvester,App.Management.Navigation, Item, Persistent, Implicit):
    """ """

    meta_type = 'Exist Open Archive Harvester'
    default_document = 'index_html'
    default_encoding = 'UTF-8'

    manage_options= (
        {'label': 'Preferences',     
         'action': 'manage_preferences' 
         },
        
        {'label': 'Update',     
         'action': 'manage_update'
         },
        
        {'label': 'Contents',     
         'action': 'manage_main'
         },
        )

    
    def __init__(self, id, host, url, title, days):
        """ """

        try:
            OAIHarvester.__init__(self, host, url)
        except:
            # this is needed for some reason when python
            # version is < 2.2
            OAIHarvester.__init__.im_func(self, host, url)
        
        self.id = id
        self.title = title

        # update frequency in days
        self.update_period = days

    def manage_afterAdd(self, item, container):
        """ redef """
        # Collection creation for record save
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        eda.createColl(eXAgg.getExistCollRoot()+'/'+self.id)

    def manage_beforeDelete(self, item, container):
        """ redef """
        # Collection delete
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        eda.delColl(eXAgg.getExistCollRoot()+'/'+self.id)
               
        
    def get_myContainer(self):
        """ get my parent container """
        return self.aq_parent

    def handle_addOAIRecord(self, dom=None):
        """
        create or update <record> given its DOM node
        """
       
        # get record header
        #
        the_xml = dom.toxml('UTF-8')
        
        header = None
        for h in dom.childNodes:
            if hasattr(h, 'tagName') and h.tagName == 'header':
                header = h
                break

        if header == None:
            raise "no header in", dom.toxml(self.default_decoding)

        # get and process ID from record header, use
        #   the id as the name for the zope record
        #
        id = None
        for tag in header.childNodes:
            if hasattr(tag, 'tagName') and tag.tagName == 'identifier':
                id = tag
                break

        if id == None:
            raise "no identifier in ", dom.toxml(self.default_decoding)
        else:
            identifier = self.getDOMElementText(id, encode=self.default_encoding)

        # treat identifier
        #
        if not identifier:
            identifier = str(DateTime().millis()) + str(random.randint(1, 10000))
            
        
        metadata_format = self.current_request['metadataPrefix'].encode(self.default_encoding)
        identifier = string.strip(identifier)
        identifier = identifier.encode(self.default_encoding) + '-' + metadata_format
        identifier = zOAISupport.processId(identifier)

        nsInfos = self.get_namespaceInfoByPrefix(metadata_format)
        rootNode = nsInfos.get('rootNode', '')
        # take the first "possibleRootNode" for oai rootNode replacement --> eXist storage
        newRootNode = nsInfos.get('possibleRootNode', [])[0]
        if rootNode:
            try:
                metadataDom = dom.getElementsByTagName('metadata')[0]
            except:
                metadataDom = dom
            try:
                for child in metadataDom.childNodes:
                    if child.localName == rootNode:
                        metadataNode = child
                        break               
            except:
                raise "no MD found in ", metadataDom.toxml(self.default_encoding)
            

        xmlBody = ''
        for child in metadataNode.childNodes:
            xmlBody += child.toxml(self.default_encoding)
        newXML = """<?xml version="1.0" encoding="%(encoding)s"?>
        <%(tag)s xmlns:%(nsDec)s>
          %(xmlBody)s
        </%(tag)s>""" % { 'encoding':self.default_encoding,
                          'tag':newRootNode,
                          'nsDec':nsInfos.get('nsDeclaration', ''),
                          'xmlBody':xmlBody,
                          }
       

        # the only thing to do is to save record in eXistDB
        eXAgg = self.get_myContainer()
        eda = eXAgg.get_eXistDA()
        nomXML = 'xmldb:exist://' + eda.server + ":" + eda.port + self.get_myContainer().getExistCollRoot()+'/'+self.id+'/'+identifier
        try:
            error = eda.saveDoc(newXML, nomXML, overwrite=1, object_only = 1)
        except:
            
            #import traceback
            #traceback.print_exc()
            pass



    ######################
    ####  ZMI Interfaces
    ######################

    #manage_main = HTMLFile("dtml/manage_OAIHarvesterMainForm",globals())

    
    manage_preferences = HTMLFile("dtml/manage_OAIHarvesterPrefsForm",globals())
    manage_update = HTMLFile("dtml/manage_OAIHarvesterUpdateForm",globals())
    
    manage_main = manage_update

    def manage_OAIHarvesterPrefs(self, title, minutes, site_host, site_url, REQUEST=None, RESPONSE=None):
        """ save preferences """

        self.title = title
        self.update_period = minutes
        self.set_siteURL(site_url)
        self.set_siteHost(site_host)

        RESPONSE.redirect(self.absolute_url() + '/manage_preferences?manage_tabs_message=Settings%20saved')

        
    

    def manage_OAIHarvesterUpdate(self, REQUEST=None, RESPONSE=None):
        """ update site records, identification """

        try:
            self.do_updateSite()
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Site%20records%20updated')
        except (HTTPLibError, ServerError):
            # import sys
            
            RESPONSE.redirect(self.absolute_url() + '/manage_update?manage_tabs_message=Problem%20connecting%20to%20site')

    

