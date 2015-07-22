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

#Product imports

# Types of portlets:
PORTLETS_TYPES = {
    0: 'Static HTML',
    1: 'Links list',
    2: 'Remote channel',
    3: 'Local channel',
    4: 'Folder',
    5: 'Script channel',
    6: 'Remote channel facade',
    7: 'Remote channel aggregator',
    99: 'Other',
    100: 'Special'
}

#used for portlets that contains static HTML code
DEFAULT_PORTLET_HEADER = '''<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span i18n:translate="" tal:replace="template/title" /></tal:block>
<tal:block metal:fill-slot="portlet_content">'''
DEFAULT_PORTLET_FOOTER = '''</tal:block>
</tal:block>'''

#used to generate portlets for other types of objects: links list, rdf channels, folders etc.
SIMPLE_PORTLET_TEMPLATE = '''<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title">PORTLET_TITLE</tal:block>
<tal:block metal:fill-slot="portlet_content">PORTLET_CONTENT</tal:block>
</tal:block>'''

HTML_PORTLET_TEMPLATE = '''<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span tal:replace="here/title" /></tal:block>
<tal:block metal:fill-slot="portlet_content"><span tal:replace="structure here/body" /></tal:block>
</tal:block>'''

LINKSLIST_PORTLET_TEMPLATE = '''<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span tal:replace="python:here.getPortletsTool().PORTLET_LINKSLIST_ID.title_or_id()" /></tal:block>
<tal:block metal:fill-slot="portlet_content">
	<ul>
	<tal:block tal:repeat="item python:here.getPortletsTool().PORTLET_LINKSLIST_ID.get_links_list()">
		<li tal:condition="python:here.checkPermissionForLink(item.permission, here)">
			<a tal:attributes="href python:test(item.relative, '%s%s' % (here.getSitePath(), item.url), item.url); title item/description" i18n:attributes="title" i18n:translate="" tal:content="item/title" />
		</li>
	</tal:block>
	</ul>
</tal:block>
</tal:block>'''

REMOTECHANNEL_PORTLET_TEMPLATE = '''<tal:block define="title python:here.getSyndicationTool()['PORTLET_REMOTECHANNEL_ID'].title_or_id();
		   items python:here.getSyndicationTool()['PORTLET_REMOTECHANNEL_ID'].getChannelItems()"
		   condition="items">
<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span tal:content="title" /></tal:block>
<tal:block metal:fill-slot="portlet_content">
	<ul>
		<li tal:repeat="item items">
			<a tal:attributes="href python:test(item.has_key('link'), item['link'], '')" tal:content="python:item['title']" />
		</li>
	</ul>
	<div style="text-align: right;">
	<a tal:attributes="href string:${here/absolute_url}/channel_details_html?id_channel=PORTLET_REMOTECHANNEL_ID">
		<span i18n:translate="">More...</span>
	</a>
	</div>
</tal:block>
</tal:block>
</tal:block>'''

LOCALCHANNEL_PORTLET_TEMPLATE = '''<tal:block tal:define="channel python:here.getSyndicationTool().PORTLET_LOCALCHANNEL_ID">
<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span i18n:translate="" tal:content="channel/title_or_id" /></tal:block>
<tal:block metal:fill-slot="portlet_content">
	<ul>
		<li tal:repeat="item channel/get_objects_for_rdf">
			<img tal:attributes="src item/icon; alt item/meta_type; title item/meta_type" style="vertical-align: -5px;" />
			<a tal:attributes="href item/absolute_url; title item/description" tal:content="item/title_or_id" />
		</li>
	</ul>
	<a tal:attributes="href channel/absolute_url"><img src="misc_/NaayaCore/xml.png" alt="Syndication (XML)" i18n:attributes="alt" /></a>
</tal:block>
</tal:block>
</tal:block>'''

FOLDER_PORTLET_TEMPLATE = '''<tal:block tal:define="folder python:here.getFolderByPath('PORTLET_FOLDER_PATH')">
<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><a tal:attributes="href folder/absolute_url" tal:content="folder/title_or_id" /></tal:block>
<tal:block metal:fill-slot="portlet_content" tal:content="structure folder/description"></tal:block>
</tal:block>
</tal:block>'''

SCRIPTCHANNEL_PORTLET_TEMPLATE = '''<tal:block tal:define="channel python:here.getSyndicationTool().PORTLET_SCRIPTCHANNEL_ID">
<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span tal:replace="channel/title_or_id" /></tal:block>
<tal:block metal:fill-slot="portlet_content">
	<ul>
		<li tal:repeat="item channel/get_objects_for_rdf">
			<img tal:attributes="src item/icon; alt item/meta_type; title item/meta_type" style="vertical-align: -5px;" />
			<a tal:attributes="href item/absolute_url; title item/description" tal:content="item/title_or_id" />
			<span tal:replace="structure item/description" />
		</li>
	</ul>
	<a tal:attributes="href channel/absolute_url"><img src="misc_/NaayaCore/xml.png" alt="Syndication (XML)" i18n:attributes="alt" /></a>
</tal:block>
</tal:block>
</tal:block>'''

CHANNEL_AGGREGATOR_PORTLET_TEMPLATE = '''<tal:block define="title python:here.getSyndicationTool()['PORTLET_AGGREGATOR_ID'].title_or_id();
		   items python:here.getSyndicationTool()['PORTLET_AGGREGATOR_ID'].getRemoteChannelsItems()"
		   condition="not:python:items == [[], []]">
<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById(portlet_macro).macros['portlet']">
<tal:block metal:fill-slot="portlet_title"><span tal:content="title" /></tal:block>
<tal:block metal:fill-slot="portlet_content">
	<ul>
		<tal:block tal:repeat="channel items">
			<li tal:repeat="item channel" ><a tal:attributes="href python:test(item.has_key('link'), item['link'], '')" tal:content="python:item['title']" /></li>
		</tal:block>
	</ul>
	<div style="text-align: right;">
	<a tal:attributes="href string:${here/absolute_url}/channel_details_html?id_channel=PORTLET_AGGREGATOR_ID">
		<span i18n:translate="">More...</span>
	</a>
	</div>
</tal:block>
</tal:block>
</tal:block>'''


PORTLETS_BODIES = {
    0: HTML_PORTLET_TEMPLATE,
    1: LINKSLIST_PORTLET_TEMPLATE,
    2: REMOTECHANNEL_PORTLET_TEMPLATE,
    3: LOCALCHANNEL_PORTLET_TEMPLATE,
    4: FOLDER_PORTLET_TEMPLATE,
    5: SCRIPTCHANNEL_PORTLET_TEMPLATE,
    6: REMOTECHANNEL_PORTLET_TEMPLATE,
    7: CHANNEL_AGGREGATOR_PORTLET_TEMPLATE,
    99: SIMPLE_PORTLET_TEMPLATE,
    100: SIMPLE_PORTLET_TEMPLATE
}
