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

__doc__ = """ Zope Exist OAI Templates """

#######  general  Templates #############
namespaceTemplate = 'declare namespace %s;\n'

queryTemplate_T = """xquery version "1.0";
%(nsdeclaration)s
let $col := collection('%(mdlocation)s')
%(letSequence)s
return transform:transform(%(resTemplate)s, %(xslFilter)s , ())"""

queryTemplate_F = """xquery version "1.0";
%(nsdeclaration)s
%(function)s
let $col := collection('%(mdlocation)s')
%(letSequence)s
let $md2 := local:prepareBlock($md1[position()>=%(start)s and position()<=%(stop)s])
return <records len="{count($md1)}">{$md2}</records>"""

#######  get_ListMetadataFormats  Templates #############

lmf_predicateTemplate = """let $md%(indice)s := name($col//%(rootNode)s[%(idPath)s &= '%(identifier)s'])\n"""

lmf_resTemplate = "<rootNode>{$md%s}</rootNode>" 

xslExtractPrefix = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format"><xsl:output method="html"/>
<xsl:template match="metadataPrefix">
      <xsl:for-each select="rootNode"><xsl:value-of select="." /></xsl:for-each>
      </xsl:template>
    </xsl:stylesheet>"""

#######  get_GetRecord Templates #############
gr_predicateTemplate = """let $md%(indice)s := local:prepareBlock($col//%(rootNode)s[%(idPath)s &= '%(identifier)s'])\n"""

gr_resTemplate = "{$md%s}"

gr_function = """declare namespace xmldb="http://exist-db.org/xquery/xmldb";
declare namespace util="http://exist-db.org/xquery/util";

declare function local:prepareBlock($nodes as node()*) as node()*{
for $md in $nodes
let $IDHeader := <identifier>%(identifier)s</identifier>
let $date := xmldb:last-modified(util:collection-name($md),util:document-name($md))
let $dateHeader := <datestamp>{year-from-dateTime($date)}-{month-from-dateTime($date)}-{day-from-dateTime($date)}</datestamp>
let $body := <%(oai_rootNode)s xmlns:%(oai_ns)s xmlns:%(md_ns)s>{$md/*}</%(oai_rootNode)s>
return <record><header>{$IDHeader}{$dateHeader}</header><metadata>{$body}</metadata></record>
};"""


###### Regular expression Template #########
import re
re_extractRecord = re.compile("(<header>(?:.*?)</header>)\s*(<metadata>(?:.*?)</metadata>)", re.MULTILINE | re.DOTALL)
re_extractRecords = re.compile("(<record>(?:.*?)</record>)", re.MULTILINE | re.DOTALL)
re_extractLenOfRecords = re.compile('<records len="(.*?)">', re.MULTILINE | re.DOTALL)

###### About Informations when sending records ########
# you can put informations here as describe in the OAI Protocol
# see http://www.openarchives.org/OAI/openarchivesprotocol.html
about_infos = ""



#######  get_ListRecords Templates #############
lr_predicateTemplate = """let $md%(indice)s := local:prepareBlock($col//%(rootNode)s)\n"""


lr_function = """declare namespace xmldb="http://exist-db.org/xquery/xmldb";
declare namespace util="http://exist-db.org/xquery/util";

declare function local:prepareBlock($nodes as node()*) as node()*{
for $md in $nodes
let $IDHeader := <identifier>{$md/%(idPath)s[1]/text()}</identifier>
let $date := xmldb:last-modified(util:collection-name($md),util:document-name($md))
let $dateHeader := <datestamp>{year-from-dateTime($date)}-{month-from-dateTime($date)}-{day-from-dateTime($date)}</datestamp>
let $body := <%(oai_rootNode)s xmlns:%(oai_ns)s xmlns:%(md_ns)s>{$md/*}</%(oai_rootNode)s>
return <record><header>{$IDHeader}{$dateHeader}</header><metadata>{$body}</metadata><about>%(about)s</about></record>
};"""


