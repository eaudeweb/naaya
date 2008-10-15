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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


from os.path import join
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater
from Products.Naaya.constants import NAAYA_PRODUCT_PATH

CHECK_OLD_REMOTE = ('getChannelItems', 'condition="items"')
CHECK_OLD_AGGREGATOR = ('getRemoteChannelsItems', 'condition="not:python:items == [[], []]"')
NEW_REMOTE = '''<tal:block define="title python:here.getSyndicationTool()['PORTLET_REMOTECHANNEL_ID'].title_or_id();
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

NEW_AGGREGATOR = '''<tal:block define="title python:here.getSyndicationTool()['PORTLET_AGGREGATOR_ID'].title_or_id();
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

class CustomContentUpdater(NaayaContentUpdater):
    """Update remote channels and aggregator portlets"""

    _properties = NaayaContentUpdater._properties

    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update remote channels and aggregator portlets'
        self.description = 'Update remote channel portlets'

    def _get_channel_id(self, channel):
        return channel.split('id_channel=')[1].split('">')[0]

    def _verify_doc(self, doc):
        """ See super"""
        src = doc.read()
        if CHECK_OLD_REMOTE[0] in src and CHECK_OLD_REMOTE[1] not in src:
            logger.debug('Update remote channel portlet %s', doc.absolute_url())
            return doc
        if CHECK_OLD_AGGREGATOR[0] in src and CHECK_OLD_AGGREGATOR[1] not in src:
            logger.debug('Update aggregator portlet %s', doc.absolute_url())
            return doc
        return None

    def _list_updates(self):
        """ Return all portals that need update"""
        portals = self.getPortals()
        for portal in portals:
            portlets = portal['portal_portlets'].objectValues(['Naaya Portlet'])
            for portlet in portlets:
                update = self._verify_doc(portlet)
                if not update:
                    continue
                yield update

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            src = update.document_src()
            if CHECK_OLD_REMOTE[0] in src:
                content = NEW_REMOTE.replace('PORTLET_REMOTECHANNEL_ID', self._get_channel_id(src))
                update.pt_edit(text=content, content_type='text/html')
                logger.debug('Updated remote channel portlet %s', update.absolute_url())
            if CHECK_OLD_AGGREGATOR[0] in src:
                content = NEW_AGGREGATOR.replace('PORTLET_AGGREGATOR_ID', self._get_channel_id(src))
                update.pt_edit(text=content, content_type='text/html')
                logger.debug('Updated aggregator portlet %s', update.absolute_url())

def register(uid):
    return CustomContentUpdater(uid)
