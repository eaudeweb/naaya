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


""" initiailization of Zope OAI Components """

def initialize(context):
    """ init our OAI stuff """

    import ZopeOAIServer
    import ZCatalogHarvester
    import zOAIAggregator
    import zOAIHarvester
    import zOAIRecord
    import zOAIToken
    import zOAINamespace

    import zOAIExistToken
    import zOAIExistAggregator
    import zOAIExistRepository
    import zOAIExistHarvester
    import zOAIExistNamespace
    
    
    context.registerClass(
        zOAIAggregator.zOAIAggregator,
        constructors = ( zOAIAggregator.manage_addOAIAggregatorForm,
                         zOAIAggregator.manage_addOAIAggregator, ),
        icon='www/icon_object.gif'
    )
    
    context.registerClass(
        ZopeOAIServer.ZopeOAIServer,
        constructors = ( ZopeOAIServer.manage_addZopeOAIServerForm,
                         ZopeOAIServer.manage_addZopeOAIServer, ),
        icon='www/icon_object.gif'
    )
    
    context.registerClass(
        zOAIHarvester.zOAIHarvester,
        constructors = ( zOAIHarvester.manage_addOAIHarvesterForm,
                         zOAIHarvester.manage_addOAIHarvester, ),
        icon='www/icon_site.gif',
        visibility=None
    )
    
    context.registerClass(
        ZCatalogHarvester.ZCatalogHarvester,
        constructors = ( ZCatalogHarvester.manage_addZCatalogHarvesterForm,
                         ZCatalogHarvester.manage_addZCatalogHarvester, ),
        icon='www/icon_site.gif',
        visibility=None
    )

    context.registerClass(
        zOAINamespace.zOAINamespace,
        constructors = ( zOAINamespace.manage_addOAINamespaceForm,
                         zOAINamespace.manage_addOAINamespace, ),
        icon='www/icon_site.gif'
    )
    
    context.registerClass(
        zOAIRecord.zOAIRecord,
        constructors = ( zOAIRecord.manage_addOAIRecord, ),
        icon='www/icon_record.gif',
        visibility=None
    )
    
    context.registerClass(
        zOAIToken.zOAIToken,
        constructors = ( zOAIToken.manage_addOAIToken, ),
        icon='www/icon_record.gif',
        visibility=None
    )

    ## zOAIImplementation for eXist
    context.registerClass(
        zOAIExistAggregator.zOAIExistAggregator,
        constructors = ( zOAIExistAggregator.manage_addOAIExistAggregatorForm,
                         zOAIExistAggregator.manage_addOAIExistAggregator, ),
        icon='www/icon_object.gif'
    )

    context.registerClass(
        zOAIExistRepository.zOAIExistRepository,
        constructors = ( zOAIExistRepository.manage_addOAIExistRepositoryForm,
                         zOAIExistRepository.manage_addOAIExistRepository, ),
        icon='www/icon_object.gif'
    )

    context.registerClass(
        zOAIExistHarvester.zOAIExistHarvester,
        constructors = ( zOAIExistHarvester.manage_addOAIExistHarvesterForm,
                         zOAIExistHarvester.manage_addOAIExistHarvester, ),
        icon='www/icon_site.gif',
        visibility=None
    )

    context.registerClass(
        zOAIExistNamespace.zOAIExistNamespace,
        constructors = ( zOAIExistNamespace.manage_addOAIExistNamespaceForm,
                         zOAIExistNamespace.manage_addOAIExistNamespace, ),
        icon='www/icon_site.gif'
    )

    context.registerClass(
        zOAIExistToken.zOAIExistToken,
        constructors = ( zOAIExistToken.manage_addOAIExistToken, ),
        icon='www/icon_record.gif',
        visibility=None
    )
    
    
    
