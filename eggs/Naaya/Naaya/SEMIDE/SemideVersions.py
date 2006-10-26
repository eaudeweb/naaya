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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Product imports
from constants import *
from Products.Naaya.constants import *
from Products.NaayaContent import *
from Products.NaayaCore.PortletsTool.HTMLPortlet import addHTMLPortlet
from Products.NaayaCore.SyndicationTool.RemoteChannel import manage_addRemoteChannel

class SemideVersions:
    """
    Class for upgrading from one version to another.
    """

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'upgrade_13_01_2006_dragos')
    def upgrade_13_01_2006_dragos(self):
        """
        Updates for country objects.
        """
        site = self.getSite()
        skel_path = join(site.get_data_path(), 'skel')
        formstool_ob = site.getFormsTool()
        portletstool_ob = self.getPortletsTool()
        #remove  country_legislationwater from portal_forms
        try: formstool_ob.manage_delObjects(['country_legislationwater'])
        except: pass
        #update country forms
        site.manage_uninstall_pluggableitem(meta_type=METATYPE_NYCOUNTRY)
        site.manage_install_pluggableitem(meta_type=METATYPE_NYCOUNTRY)
        #update portlet_country_left
        content = self.futRead(join(skel_path, 'portlets', 'portlet_country_left.zpt'), 'r')
        portletstool_ob._getOb('portlet_country_left').pt_edit(text=content, content_type='')
        #update countries
        for country in site.countries.objectValues(METATYPE_NYCOUNTRY):
            #create RDF channels for each country
            channel = country.get_rc_legislation()
            if channel is None:
                manage_addRemoteChannel(country, id=country.get_rc_legislation_id(),
                    title='Legislation on water RSS feed')
            channel = country.get_rc_project()
            if channel is None:
                manage_addRemoteChannel(country, id=country.get_rc_project_id(),
                    title='Project water RSS feed')
            #create portlets
            portlet = country.get_portlet_indicators()
            if portlet is None:
                addHTMLPortlet(country, id=country.get_portlet_indicators_id(),
                    title='Key indicators', lang='en')
            portlet = country.get_portlet_reports()
            if portlet is None:
                addHTMLPortlet(country, id=country.get_portlet_reports_id(),
                    title='Important reports', lang='en')
            #create legislation_water folder
            legislation_water = country._getOb('legislation_water', None)
            if legislation_water is None:
                country.addNyFolder(id='legislation_water',
                    title='Legislation on water', sortorder=30,
                    publicinterface=1, folder_meta_types='')
                legislation_water = country._getOb('legislation_water', None)
            legislation_water.index.pt_edit(text="""<span tal:replace="structure here/standard_html_header" />

<div id="right_port" tal:define="items python:here.get_right_portlets_locations_objects(here)"
	tal:condition="python:len(items)>0">
	<tal:block tal:repeat="item items">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<tal:block tal:define=" isArabic here/isArabicLanguage;
						noArabic not:isArabic">
<div class="middle_port" tal:define="margin_string python:test(isArabic,'margin-left:0;;','margin-right:0;;')" tal:attributes="style python:test(here.getPortletsTool().get_right_portlets_locations_objects(here), '', margin_string)">
<h1>
	<img tal:attributes="src python:test(here.approved, here.icon, here.icon_marked); title here/meta_type; alt here/meta_type" border="0" />
	<tal:block tal:replace="here/title_or_id" />
	<tal:block tal:condition="here/can_be_seen">
		<tal:block tal:condition="here/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h1>
<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<div id="admin_this_folder" tal:condition="here/checkPermissionEditObject">
	<a tal:attributes="href string:${here/absolute_url}/edit_html"><span i18n:translate="">Edit Folder</span></a>
	<a tal:attributes="href string:${here/absolute_url}/update_legislation_feed"><span i18n:translate="">Update feed</span></a>
</div>

<tal:block tal:define="channel here/get_rc_legislation">
<tal:block tal:condition="channel/get_feed_bozo_exception">
<strong i18n:translate="">Error</strong>: <span tal:replace="channel/get_feed_bozo_exception" /><br />
</tal:block>

<tal:block tal:condition="python:not channel.get_feed_bozo_exception()">
<ul tal:condition="python:channel.count_feed_items()>0">
	<li tal:repeat="item channel/getChannelItems">
		<a tal:attributes="href python:item['link']"
			tal:content="python:item['title']" />
	</li>
</ul>
</tal:block>
<strong tal:condition="python:channel.count_feed_items()<=0" i18n:translate="">
	No data available.
</strong>
</tal:block>

<span tal:replace="structure here/comments_box" />

</div>
</tal:block>
<span tal:replace="structure here/standard_html_footer"/>""", content_type='')
            #update project_water folder
            project_water = country._getOb('project_water', None)
            if project_water is None:
                country.addNyFolder(id='project_water',
                    title='Project water', sortorder=40,
                    publicinterface=1, folder_meta_types='')
                project_water = country._getOb('project_water', None)
            project_water.publicinterface = 1
            project_water._p_changed = 1
            project_water.createPublicInterface()
            project_water.index.pt_edit(text="""<span tal:replace="structure here/standard_html_header" />

<tal:block define="objects_info here/checkPermissionManageObjects;
	folders_list python:objects_info[6];
	objects_list python:objects_info[7];
	btn_select python:objects_info[0];
	btn_delete python:objects_info[1];
	btn_copy python:objects_info[2];
	btn_cut python:objects_info[3];
	btn_paste python:objects_info[4];
	can_operate python:objects_info[5] ">

<script language="javascript" type="text/javascript" tal:condition="btn_select">
<!--
var isSelected = false;
function toggleSelect()
{   var frm = document.objectItems;
    var i;
    if (isSelected == false)
    {   for(i=0; i<frm.elements.length; i++)
            if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'id') frm.elements[i].checked = true;
        isSelected = true;}
    else
    {   for(i=0; i<frm.elements.length; i++)
            if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'id') frm.elements[i].checked = false;
        isSelected = false;}}

function fCheckSelection()
{   var frm = document.objectItems;
    var i;
    check = false;
    for(i=0; i<frm.elements.length; i++)
        if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
        {   check = true; break;}
    return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_copy">
<!--
function fCopyObjects()
{   if (fCheckSelection())
    {   document.objectItems.action="copyObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to copy.');}
//-->
</script>


<script language="javascript" type="text/javascript" tal:condition="btn_cut">
<!--
function fCutObjects()
{   if (fCheckSelection())
    {
        document.objectItems.action="cutObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to cut.');}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_paste">
<!--
function fPasteObjects()
{   document.objectItems.action="pasteObjects";
    document.objectItems.submit();}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_delete">
<!--
function fDeleteObjects()
{   if (fCheckSelection())
    {   document.objectItems.action="deleteObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to delete.');}
//-->
</script>

<div id="right_port" tal:define="items python:here.get_right_portlets_locations_objects(here)"
	tal:condition="python:len(items)>0">
	<tal:block tal:repeat="item items">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<tal:block tal:define=" isArabic here/isArabicLanguage;
						noArabic not:isArabic">
<div class="middle_port" tal:define="margin_string python:test(isArabic,'margin-left:0;;','margin-right:0;;')" tal:attributes="style python:test(here.getPortletsTool().get_right_portlets_locations_objects(here), '', margin_string)">
<h1>
	<img tal:attributes="src python:test(here.approved, here.icon, here.icon_marked); title here/meta_label; alt here/meta_label" border="0" />
	<tal:block tal:replace="here/title_or_id" />
	<tal:block tal:condition="here/can_be_seen">
		<tal:block tal:condition="here/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h1>
<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<tal:block tal:define="this_absolute_url python:here.absolute_url(0);
	submissions here/process_submissions;
	perm_add_something python:len(submissions)>0;
	perm_edit_object here/checkPermissionEditObject;
	perm_publish_objects here/checkPermissionPublishObjects;
	perm_validate_objects here/checkPermissionValidateObjects">
<div id="admin_this_folder" tal:condition="python:perm_add_something or perm_edit_object and perm_publish_objects or perm_validate_objects">
	<span id="submission" tal:condition="perm_add_something">
		<span i18n:translate="" tal:omit-tag="">Submit</span>:
		<select name="typetoadd"
			tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
			<option value="#" i18n:translate="">Type to add</option>
			<option tal:repeat="item submissions"
				tal:attributes="value python:item[0]"
				tal:content="python:item[1]" i18n:translate="" />
		</select>
	</span>
	<tal:block tal:condition="python:perm_edit_object or perm_publish_objects or perm_validate_objects">
		<a tal:condition="python:perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span i18n:translate="">Edit Folder</span></a>
		<a tal:condition="python:perm_edit_object" tal:attributes="href string:${this_absolute_url}/update_project_feed"><span i18n:translate="">Update feed</span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
		<a tal:condition="perm_validate_objects" tal:attributes="href string:${this_absolute_url}/basketofvalidation_html"><span i18n:translate="">Validation</span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/sortorder_html"><span i18n:translate="">Sort order</span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/restrict_html"><span i18n:translate="">Restrict</span></a>
	</tal:block>
</div>
</tal:block>

<tal:block tal:define="channel here/get_rc_project">
<tal:block tal:condition="channel/get_feed_bozo_exception">
<strong i18n:translate="">Error</strong>: <span tal:replace="channel/get_feed_bozo_exception" /><br />
</tal:block>

<tal:block tal:condition="python:not channel.get_feed_bozo_exception()">
<ul tal:condition="python:channel.count_feed_items()>0">
	<li tal:repeat="item channel/getChannelItems">
		<a tal:attributes="href python:item['link']"
			tal:content="python:item['title']" />
	</li>
</ul>
</tal:block>
<strong tal:condition="python:channel.count_feed_items()<=0" i18n:translate="">
	No data available.
</strong>
</tal:block>

<div tal:condition="python:btn_select or btn_delete or btn_copy or btn_cut or btn_paste">
	<div id="toolbar">
		<tal:block tal:condition="btn_select">
			<input type="reset" onclick="toggleSelect();return false" i18n:attributes="value" value="Select all" />
				<img tal:condition="python:False" src="/misc_/Naaya/select_all.gif" border="0" alt="Select all" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_copy">
			<input type="reset" onclick="fCopyObjects();return false" i18n:attributes="value" value="Copy" />
				<img tal:condition="python:False" src="/misc_/Naaya/copy.gif" border="0" alt="Copy" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_cut">
			<input type="reset" onclick="fCutObjects();return false" i18n:attributes="value" value="Cut" />
				<img tal:condition="python:False" src="/misc_/Naaya/cut.gif" border="0" alt="Cut" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_paste">
			<input type="reset" onclick="fPasteObjects();return false" i18n:attributes="value" value="Paste" />
				<img tal:condition="python:False" src="/misc_/Naaya/paste.gif" border="0" alt="Paste" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_delete">
			<input type="reset" onclick="fDeleteObjects();return false" i18n:attributes="value" value="Delete" />
				<img tal:condition="python:False" src="/misc_/Naaya/delete.gif" border="0" alt="Delete" i18n:attributes="alt" />
		</tal:block>
	</div>
</div>

<form name="objectItems" method="post" action="">
<table border="0" cellpadding="0" cellspacing="0" id="folderfile_list">
<tr tal:condition="can_operate">
	<th class="checkbox" style="width: 4%;" i18n:translate="" tal:condition="btn_select"></th>
	<th class="type" style="width: 4%;" i18n:translate="">Type</th>
	<th class="title-column" i18n:translate="">Title</th>
	<th class="checkin" i18n:translate="">Version</th>
	<th class="edit" i18n:translate="">Edit</th>
</tr>
<tr tal:repeat="folders folders_list">
	<tal:block define="del_permission python:folders[0];
		edit_permission python:folders[1];
		version_status python:folders[2];
		copy_permission python:folders[3];
		folder python:folders[4]">
	<td class="checkbox" tal:condition="btn_select" style="width: 4%; vertical-align: top;"><input tal:condition="python:del_permission or edit_permission or copy_permission" type="checkbox" name="id" tal:attributes="value folder/id" /></td>
	<td class="type" style="width: 4%;"><img tal:attributes="src python:test(folder.approved, folder.icon, folder.icon_marked); alt folder/meta_type; title folder/meta_type" border="0" /></td>
	<td class="title-column">
		<a tal:attributes="href folder/absolute_url" tal:content="folder/title_or_id" />
		<tal:block tal:condition="folder/can_be_seen">
			<tal:block tal:condition="folder/has_restrictions" i18n:translate="">
				[Limited access]
			</tal:block>
		</tal:block>
		<tal:block tal:condition="python:not folder.can_be_seen()" i18n:translate="">
			[Restricted access]
		</tal:block>
		<tal:block tal:condition="python:folder.is_open_for_comments() and folder.count_comments()>0">
			[<span tal:replace="folder/count_comments" />
			<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
		</tal:block>
		<tal:block condition="python:False" replace="structure folder/description" />
	</td>
	<td class="checkin" tal:condition="can_operate" i18n:translate="">n/a</td>
	<td class="edit" tal:condition="can_operate">
		<a tal:condition="edit_permission" tal:attributes="href string:${folder/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
		<tal:block tal:condition="python:not edit_permission" i18n:translate="">n/a</tal:block>
	</td>
	</tal:block>
</tr>
<tr tal:repeat="objects objects_list">
	<tal:block define="del_permission python:objects[0];
			edit_permission python:objects[1];
			version_status python:objects[2];
			copy_permission python:objects[3];
			object python:objects[4]">
	<td class="checkbox" tal:condition="btn_select" style="width: 4%; vertical-align: top;"><input tal:condition="python:del_permission or edit_permission or copy_permission" type="checkbox" name="id" tal:attributes="value object/id" /></td>
	<td class="type" style="width: 4%;"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt object/meta_type; title object/meta_type" border="0" /></td>
	<td class="title-column">
		<a tal:attributes="href object/absolute_url" tal:content="object/title_or_id" />
		<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
			[<span tal:replace="object/count_comments" />
			<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
		</tal:block>
		<span tal:replace="structure object/description" />
	</td>
	<td class="checkin" tal:condition="can_operate">
		<tal:block tal:condition="python:version_status == 0" i18n:translate="">n/a</tal:block>
		<a tal:condition="python:version_status == 2" tal:attributes="href string:${object/absolute_url}/startVersion"><img src="misc_/Naaya/checkout" border="0" alt="Checkout - start new version" i18n:attributes="alt" /></a>
		<a tal:condition="python:version_status == 1" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/checkin" border="0" alt="Version control" i18n:attributes="alt" /></a>
	</td>
	<td class="edit" tal:condition="can_operate">
		<a tal:condition="python:edit_permission and not object.hasVersion()" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
		<tal:block tal:condition="python:edit_permission and object.hasVersion() or not edit_permission" i18n:translate="">n/a</tal:block>
	</td>
	</tal:block>
</tr>
</table>
</form>

<p><a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a></p>
<span tal:replace="structure here/comments_box" />

</div>
</tal:block>
</tal:block>
<span tal:replace="structure here/standard_html_footer"/>""", content_type='')
        return "upgrade_13_01_2006_dragos: OK"

    security.declareProtected(view_management_screens, 'issues_20_01_2006_dragos')
    def issues_20_01_2006_dragos(self):
        """
        Scripts for solving reported issues.
        """
        site = self.getSite()
        skel_path = join(site.get_data_path(), 'skel')
        #install Naaya Semide Project
        try: site.manage_install_pluggableitem(meta_type=METATYPE_NYSEMPROJECT)
        except: pass
        portletstool_ob = self.getPortletsTool()
        formstool_ob = site.getFormsTool()
        #issue: Country template - Links
        #issue: Country template - Contacts folder
        #issue: Country - data and statistics subfolder
        # - for each country update Links folder subobjects
        # - for each country update Contacts folder subobjects
        # - for each country update Date and Statistics folder subobjects
        # - for each country update custom_header and custom_footer
        for country in site.countries.objectValues(METATYPE_NYCOUNTRY):
            links = country._getOb('links', None)
            links.folder_meta_types = [METATYPE_FOLDER, METATYPE_NYURL]
            links._p_changed = 1
            contacts = country._getOb('contacts', None)
            contacts.folder_meta_types = [METATYPE_NYURL]
            contacts._p_changed = 1
            data_statistics = country._getOb('data_statistics', None)
            data_statistics.folder_meta_types = [METATYPE_FOLDER, METATYPE_NYFILE, METATYPE_NYURL]
            data_statistics._p_changed = 1
            country.custom_header.pt_edit(text="""<tal:block define="site here/getSite">
<span tal:replace="structure site/standard_html_header" />

<div id="right_port" tal:define="items here/get_right_portlets_objects"
	tal:condition="python:len(items)>0">
	<tal:block tal:repeat="item items">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<tal:block
	tal:define="isArabic here/isArabicLanguage; noArabic not:isArabic;
				country here/get_country_object">
<div class="middle_port" tal:define="margin_string python:test(isArabic,'margin-left:0;;','margin-right:0;;')" tal:attributes="style python:test(here.getPortletsTool().get_right_portlets_locations_objects(here), '', margin_string)">
<div style="float:right;" tal:condition="country/hasSmallFlag">
	<img tal:attributes="src string:${country/absolute_url}/getSmallFlag;alt country/title_or_id" />
</div>
<h2 class="country-title">
	<tal:block tal:replace="country/title_or_id" />
	<tal:block tal:condition="country/can_be_seen">
		<tal:block tal:condition="country/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not country.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h2>
<div id="admin_this_folder" tal:condition="python:show_edit==1 and country.checkPermissionEditObject()"
	tal:define="portlet_indicators country/get_portlet_indicators;
				portlet_reports country/get_portlet_reports">
	<a tal:attributes="href string:${country/absolute_url}/edit_html"><span i18n:translate="">Edit country</span></a>
	<a tal:condition="python:portlet_indicators is not None" tal:attributes="href string:${country/absolute_url}/editportlet_html?id=${portlet_indicators/id}"><span><span i18n:translate="" tal:omit-tag="">Edit</span> <span tal:replace="portlet_indicators/title_or_id" /><span/></a>
	<a tal:condition="python:portlet_reports is not None" tal:attributes="href string:${country/absolute_url}/editportlet_html?id=${portlet_reports/id}"><span><span i18n:translate="" tal:omit-tag="">Edit</span> <span tal:replace="portlet_reports/title_or_id" /><span/></a>
</div>
<p tal:condition="python:country.description!=''" tal:content="structure country/description" />
</div>

	<!--SITE_HEADERFOOTER_MARKER-->

</tal:block>
</tal:block>""", content_type='')
            country.custom_footer.pt_edit(text="""<tal:block define="site here/getSite">

	<!--SITE_HEADERFOOTER_MARKER-->

<span tal:replace="structure site/standard_html_footer" />
</tal:block>""", content_type='')
            project_water = country._getOb('project_water', None)
            project_water.folder_meta_types = [METATYPE_NYSEMPROJECT]
            project_water._p_changed = 1
        #issue: Events/News related with country portlets
        # - remove portlet_country_latestnews and portlet_country_upcomingevents from portlets tool
        try: portletstool_ob.manage_delObjects(['portlet_country_latestnews', 'portlet_country_upcomingevents'])
        except: pass
        #issue: Country template - NFP website links
        site.manage_uninstall_pluggableitem(meta_type=METATYPE_NYCOUNTRY)
        site.manage_install_pluggableitem(meta_type=METATYPE_NYCOUNTRY)
        content = self.futRead(join(skel_path, 'portlets', 'portlet_country_left.zpt'), 'r')
        portletstool_ob._getOb('portlet_country_left').pt_edit(text=content, content_type='')
        #issue: Countries - Classifying countries
        # - update Countries folder subobjects
        countries = site._getOb('countries', None)
        countries.folder_meta_types = [METATYPE_FOLDER, METATYPE_NYCOUNTRY]
        countries.publicinterface = 0
        countries._p_changed = 1
        try: countries.manage_delObjects(['index'])
        except: pass
        #issue: Country template - Page layout
        # - update folder_index
        # - update site search
        content = self.futRead(join(skel_path, 'forms', 'folder_index.zpt'), 'r')
        formstool_ob._getOb('folder_index').pt_edit(text=content, content_type='')
        content = self.futRead(join(skel_path, 'forms', 'site_search.zpt'), 'r')
        formstool_ob._getOb('site_search').pt_edit(text=content, content_type='')
        content = self.futRead(join(skel_path, 'forms', 'site_index.zpt'), 'r')
        formstool_ob._getOb('site_index').pt_edit(text=content, content_type='')
        return "issues_20_01_2006_dragos: OK"


    security.declareProtected(view_management_screens, 'issues_06_06_2006')
    def issues_06_06_2006(self):
        """ """

        project_water_index = """<span tal:replace="structure here/standard_html_header" />

<tal:block define="objects_info here/checkPermissionManageObjects;
	folders_list python:objects_info[6];
	objects_list python:objects_info[7];
	btn_select python:objects_info[0];
	btn_delete python:objects_info[1];
	btn_copy python:objects_info[2];
	btn_cut python:objects_info[3];
	btn_paste python:objects_info[4];
	can_operate python:objects_info[5] ">

<script language="javascript" type="text/javascript" tal:condition="btn_select">
<!--
var isSelected = false;
function toggleSelect()
{   var frm = document.objectItems;
var i;
if (isSelected == false)
{   for(i=0; i<frm.elements.length; i++)
if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'id') frm.elements[i].checked = true;
isSelected = true;}
else
{   for(i=0; i<frm.elements.length; i++)
if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'id') frm.elements[i].checked = false;
isSelected = false;}}

function fCheckSelection()
{   var frm = document.objectItems;
var i;
check = false;
for(i=0; i<frm.elements.length; i++)
if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
{   check = true; break;}
return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_copy">
<!--
function fCopyObjects()
{   if (fCheckSelection())
{   document.objectItems.action="copyObjects";
document.objectItems.submit();}
else
alert('Please select one or more items to copy.');}
//-->
</script>


<script language="javascript" type="text/javascript" tal:condition="btn_cut">
<!--
function fCutObjects()
{   if (fCheckSelection())
{
document.objectItems.action="cutObjects";
document.objectItems.submit();}
else
alert('Please select one or more items to cut.');}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_paste">
<!--
function fPasteObjects()
{   document.objectItems.action="pasteObjects";
document.objectItems.submit();}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_delete">
<!--
function fDeleteObjects()
{   if (fCheckSelection())
{   document.objectItems.action="deleteObjects";
document.objectItems.submit();}
else
alert('Please select one or more items to delete.');}
//-->
</script>

<div id="right_port" tal:define="items python:here.get_right_portlets_locations_objects(here)"
	tal:condition="python:len(items)>0">
	<tal:block tal:repeat="item items">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<tal:block tal:define=" isArabic here/isArabicLanguage;
						noArabic not:isArabic">
<div class="middle_port">
<h1>
	<img tal:attributes="src python:test(here.approved, here.icon, here.icon_marked); title here/meta_label; alt here/meta_label" border="0" />
	<tal:block tal:replace="here/title_or_id" />
	<tal:block tal:condition="here/can_be_seen">
		<tal:block tal:condition="here/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h1>
<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<tal:block tal:define="this_absolute_url python:here.absolute_url(0);
	submissions here/process_submissions;
	perm_add_something python:len(submissions)>0;
	perm_edit_object here/checkPermissionEditObject;
	perm_publish_objects here/checkPermissionPublishObjects;
	perm_validate_objects here/checkPermissionValidateObjects">
<div id="admin_this_folder" tal:condition="python:perm_add_something or perm_edit_object and perm_publish_objects or perm_validate_objects">
	<span id="submission" tal:condition="perm_add_something">
		<span i18n:translate="" tal:omit-tag="">Submit</span>:
		<select name="typetoadd"
			tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
			<option value="#" i18n:translate="">Type to add</option>
			<option tal:repeat="item submissions"
				tal:attributes="value python:item[0]"
				tal:content="python:item[1]" i18n:translate="" />
		</select>
	</span>
	<tal:block tal:condition="python:perm_edit_object or perm_publish_objects or perm_validate_objects">
		<a tal:condition="python:perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span i18n:translate="">Edit folder</span></a>
		<a tal:condition="python:perm_edit_object" tal:attributes="href string:${this_absolute_url}/update_project_feed"><span i18n:translate="">Update feed</span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
		<a tal:condition="perm_validate_objects" tal:attributes="href string:${this_absolute_url}/basketofvalidation_html"><span i18n:translate="">Validation</span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/sortorder_html"><span i18n:translate="">Sort order</span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/restrict_html"><span i18n:translate="">Restrict</span></a>
	</tal:block>
</div>
</tal:block>

<tal:block tal:define="channel here/get_rc_project">
<tal:block tal:condition="python:not channel.get_feed_bozo_exception()">
<ul tal:condition="python:channel.count_feed_items()>0">
	<li tal:repeat="item channel/getChannelItems">
		<a tal:attributes="href python:item['link']"
			tal:content="python:item['title']" />
	</li>
</ul>
</tal:block>
<strong tal:condition="python:channel.count_feed_items()<=0" i18n:translate="">
	No data available.
</strong>
</tal:block>

<div tal:condition="python:btn_select or btn_delete or btn_copy or btn_cut or btn_paste">
	<div id="toolbar">
		<tal:block tal:condition="btn_select">
			<input type="reset" onclick="toggleSelect();return false" i18n:attributes="value" value="Select all" />
				<img tal:condition="python:False" src="/misc_/Naaya/select_all.gif" border="0" alt="Select all" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_copy">
			<input type="reset" onclick="fCopyObjects();return false" i18n:attributes="value" value="Copy" />
				<img tal:condition="python:False" src="/misc_/Naaya/copy.gif" border="0" alt="Copy" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_cut">
			<input type="reset" onclick="fCutObjects();return false" i18n:attributes="value" value="Cut" />
				<img tal:condition="python:False" src="/misc_/Naaya/cut.gif" border="0" alt="Cut" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_paste">
			<input type="reset" onclick="fPasteObjects();return false" i18n:attributes="value" value="Paste" />
				<img tal:condition="python:False" src="/misc_/Naaya/paste.gif" border="0" alt="Paste" i18n:attributes="alt" />
		</tal:block>
		<tal:block tal:condition="btn_delete">
			<input type="reset" onclick="fDeleteObjects();return false" i18n:attributes="value" value="Delete" />
				<img tal:condition="python:False" src="/misc_/Naaya/delete.gif" border="0" alt="Delete" i18n:attributes="alt" />
		</tal:block>
	</div>
</div>

<tal:block	define="sq python:request.get('sq', '');
					so python:request.get('so', '');
					sel_lang python:here.gl_get_selected_language();
					sl python:here.utConvertToList(request.get('sl', [sel_lang]));
					gz python:request.get('gz', '');
					th python:request.get('th', '');
					pr python:request.get('pr', '');
					ps_start python:request.get('start', 0);
					archive python:here.getObjects();
					skey python:request.get('skey', 'start_date');
					rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
					rkey_param python:test(rkey, '', '&amp;rkey=1');

					langs_querystring python:'&sl:list='.join(sl);
					page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&so=${so}&sl:list=${langs_querystring}&gz=${gz}&th=${th}&pr=${pr};
					results python:here.getProjectsListing(sq, so, sl, skey, rkey, archive, ps_start, gz, th, pr);

					list_paging python:results[0];
					paging_start python:list_paging[0]+1;
					paging_upper python:list_paging[1];
					paging_total python:list_paging[2];
					paging_prev python:list_paging[3];
					paging_next python:list_paging[4];
					paging_current_page python:list_paging[5];
					paging_records_page python:list_paging[6];
					paging_pages python:list_paging[7];

					list_result python:results[1];
					objects_list python:list_result[2];
					objects_delete_all python:list_result[1];
					objects_select_all python:list_result[0]">

	<fieldset class="search_field"><legend i18n:translate="">Search projects</legend>
		<div class="fieldset_div">
			<form method="get" action="">
				<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
				<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
				<div class="field">
					<label for="sq" i18n:translate="">Query</label>
					<input type="text" name="sq" id="sq" size="30" tal:attributes="value sq" />
				</div>
				<div class="field">
					<label for="pr" i18n:translate="">Programme</label>
					<input type="text" name="pr" id="pr" size="30" tal:attributes="value pr" />
				</div>
				<div class="field">
					<label for="so" i18n:translate="">Organisation</label>
					<input type="text" name="so" id="so" size="30" tal:attributes="value so" />
				</div>
				<div class="field">
					<label for="th" i18n:translate="">Theme</label>
					<select name="th" id="th">
						<option value="" />
						<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(here.gl_get_selected_language())">
							<option	tal:condition="item/theme_name"
									tal:attributes="value item/theme_id;
													selected python:item.theme_id == th"
									tal:content="item/theme_name" />
							<option	tal:condition="not:item/theme_name"
									tal:attributes="value item/theme_id;
													selected python:item.theme_id == th"
									i18n:translate="">no translation available</option>
						</tal:block>
					</select>
				</div>
				<div class="field">
					<label for="gz" i18n:translate="">Country</label>
					<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
						<option value="" />
						<tal:block repeat="item langs_list">
							<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
												translation python:item.get_translation_by_language(lang_name)">
								<option	tal:condition="translation"
										tal:attributes="value item/id; selected python:item.id == gz"
										tal:content="translation" />
								<tal:block	condition="not:translation"
											define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
													def_trans python:item.get_translation_by_language(lang_name)">
									<option	tal:condition="def_trans"
											tal:attributes="value item/id; selected python:item.id == gz"
											tal:content="def_trans" />
									<option	tal:condition="not:def_trans"
											tal:attributes="value item/id; selected python:item.id == gz"
											i18n:translate="">no translation available</option>
								</tal:block>
							</tal:block>
						</tal:block>
					</select>
				</div>
				<div class="field">
					<br />
					<input type="submit" value="Search" i18n:attributes="value" />
				</div>
				<div class="clear_float"></div>
				<div class="field-inline" tal:define="selected_language here/gl_get_selected_language">
					<strong i18n:translate="">Languages: </strong>
					<tal:block repeat="item here/gl_get_languages_mapping">
						<input	name="sl" type="checkbox"
								tal:attributes="value python:item['code'];
												checked python:item['code'] in sl;
												id python:'sl_'+item['code']" />
						<label class="search_language" tal:attributes="for python:'sl_'+item['code']" tal:content="python:item['name']" />
					</tal:block>
				</div>
			</form>
		</div>
	</fieldset>

	<h2>
		<span tal:condition="python:sq=='' and so=='' and th=='' and gz=='' and pr==''" i18n:translate="">Projects</span>
		<span tal:condition="python:not(sq=='' and so=='' and th=='' and gz=='' and pr=='')" i18n:translate="">Search results</span>
	</h2>

	<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No projects available</p>
	<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
	<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
			tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
						sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
						sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
						req_params python:here.getRequestParams(request)">
		<tr>
			<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
			<th style="width: 10%;">
				<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
									title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
				<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
					 width="12" height="12" alt=""/>
				</a>
			</th>
			<th>
				<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
									title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
				<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
					 width="12" height="12" alt=""/>
				</a>
			</th>
			<th style="width: 15%;">
				<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
									title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Countries</span>
				<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
					 width="12" height="12" alt=""/>
				</a>
			</th>
			<th>
				<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=programme${rkey_param};
									title python:test(skey=='programme', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Programme</span>
				<img tal:attributes="src python:test(skey=='programme', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
					 width="12" height="12" alt=""/>
				</a>
			</th>
			<th><span i18n:translate="" title="not sortable">Link</span></th>
			<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable" i18n:attributes="title">Edit</span></th>
		</tr>
		<tr tal:repeat="objects objects_list">
			<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
				<td class="checkbox" tal:condition="del_permission" width="4%" valign="top">
					<input tal:condition="python:object in archive" type="checkbox" name="id" tal:attributes="value object/id" />
					<span tal:condition="python:not object in archive">-</span>
				</td>
				<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
				<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
				<a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
					<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
						[<span tal:replace="object/count_comments" />
						<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
					</tal:block>
				</td>
				<td tal:content="python:test(object.coverage, object.coverage, '-')" />
				<td tal:content="python:test(object.programme, object.programme, '-')" />
				<td><a tal:condition="python:object.resourceurl not in ['', 'http://']" tal:attributes="href python:test(object.resourceurl, object.resourceurl, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.resourceurl in ['', 'http://']">-</span></td>
				<td class="edit" tal:condition="edit_permission">
					<a tal:condition="python:not object.hasVersion() and object in archive" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
					<span tal:condition="python:not(not object.hasVersion() and object in archive)">-</span>
				</td>
			</tal:block>
		</tr>
	</table>
	</form>

	<p>
		Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
		Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
		<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
			tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
			<span	tal:repeat="page paging_pages">
				<a	class="paging-link-off"
					tal:condition="python:paging_current_page==page"
					tal:content="python:page+1" />
				<a	tal:condition="python:paging_current_page!=page"
					tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
					tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
					tal:content="python:page+1" />
			</span>
			<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
				<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
					tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
			</span>
	</p>
</tal:block>

<p><a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a></p>
<span tal:replace="structure here/comments_box" />

</div>
</tal:block>
</tal:block>
<span tal:replace="structure here/standard_html_footer"/>"""

        thematic_dir_index = """<span tal:replace="structure here/standard_html_header" />

<tal:block define="objects_info here/checkPermissionManageObjects;
	folders_list python:objects_info[6];
	objects_list python:objects_info[7];
	btn_select python:objects_info[0];
	btn_delete python:objects_info[1];
	btn_copy python:objects_info[2];
	btn_cut python:objects_info[3];
	btn_paste python:objects_info[4];
	can_operate python:objects_info[5];
	fld_url python:here.utUrlEncode(here.absolute_url(1));

	ps_start python:request.get('start', 0);
	skey python:request.get('skey', 'title');
	rkey python:request.get('rkey', test(request.has_key('skey'),'','0'));
	rkey_param python:test(rkey, '', '&amp;rkey=1');

	portlets_data python:here.getThDirPortletsData(skey, rkey, ps_start)">

<script language="javascript" type="text/javascript" tal:condition="btn_select">
<!--
var isSelected = false;
function toggleSelect()
{   var frm = document.objectItems;
    var i;
    if (isSelected == false)
    {   for(i=0; i<frm.elements.length; i++)
            if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'id') frm.elements[i].checked = true;
        isSelected = true;}
    else
    {   for(i=0; i<frm.elements.length; i++)
            if (frm.elements[i].type == "checkbox" && frm.elements[i].name == 'id') frm.elements[i].checked = false;
        isSelected = false;}}

function fCheckSelection()
{   var frm = document.objectItems;
    var i;
    check = false;
    for(i=0; i<frm.elements.length; i++)
        if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
        {   check = true; break;}
    return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_copy">
<!--
function fCopyObjects()
{   if (fCheckSelection())
    {   document.objectItems.action="copyObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to copy.');}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_cut">
<!--
function fCutObjects()
{   if (fCheckSelection())
    {
        document.objectItems.action="cutObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to cut.');}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_paste">
<!--
function fPasteObjects()
{   document.objectItems.action="pasteObjects";
    document.objectItems.submit();}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_delete">
<!--
function fDeleteObjects()
{   if (fCheckSelection())
    {   document.objectItems.action="deleteObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to delete.');}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="btn_copy">
<!--
function fCopyObjects()
{   if (fCheckSelection())
{   document.objectItems.action="copyObjects";
document.objectItems.submit();}
else
alert('Please select one or more items to copy.');}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="python:here.testNFPContext(here.absolute_url())">
<!--
function fDownloadObjects()
{   if (fCheckSelection())
    {   document.objectItems.action="downloadObjects";
        document.objectItems.submit();}
    else
        alert('Please select one or more items to download.');}
//-->
</script>


<div id="right_port">
	<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById('portlet_right_macro').macros['portlet']">
		<tal:block metal:fill-slot="portlet_title">
			<span i18n:translate="" tal:omit-tag="">News</span>
		</tal:block>
		<tal:block metal:fill-slot="portlet_content">
			<tal:block define="news python:portlets_data[0]">
				<ul tal:condition="news">
					<li tal:repeat="item news">
						<img tal:attributes="src item/icon; alt python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type); title python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type)" style="vertical-align: -5px;" />
						<a tal:attributes="href item/absolute_url; title item/description" tal:content="item/title_or_id" />
					</li>
				</ul>
				<span tal:condition="not:news" omit-tag="" i18n:translate="">No entries matching the filters of this folder.</span>
			</tal:block>
		</tal:block>
	</tal:block>


	<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById('portlet_right_macro').macros['portlet']">
		<tal:block metal:fill-slot="portlet_title">
			<span i18n:translate="" tal:omit-tag="">Events</span>
		</tal:block>
		<tal:block metal:fill-slot="portlet_content">
			<tal:block define="events python:portlets_data[1]">
				<ul tal:condition="events">
					<li tal:repeat="item events">
						<img tal:attributes="src item/icon; alt python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type); title python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type)" style="vertical-align: -5px;" />
						<a tal:attributes="href item/absolute_url; title item/description" tal:content="item/title_or_id" />
					</li>
				</ul>
				<span tal:condition="not:events" omit-tag="" i18n:translate="">No entries matching the filters of this folder.</span>
			</tal:block>
		</tal:block>
	</tal:block>

	<tal:block metal:use-macro="python:here.getLayoutTool().getCurrentSkin().getTemplateById('portlet_right_macro').macros['portlet']">
		<tal:block metal:fill-slot="portlet_title">
			<span i18n:translate="" tal:omit-tag="">Projects</span>
		</tal:block>
		<tal:block metal:fill-slot="portlet_content">
			<tal:block define="projects python:portlets_data[2]">
				<ul tal:condition="projects" class="proj_projects">
					<li tal:repeat="item projects">
						<img tal:attributes="src item/icon; alt python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type); title python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type)" style="vertical-align: -5px;" />
						<a tal:attributes="href item/absolute_url; title item/description" tal:content="item/title_or_id" />
					</li>
				</ul>
				<span tal:condition="not:projects" omit-tag="" i18n:translate="">No entries matching the filters of this folder.</span>
			</tal:block>
		</tal:block>
	</tal:block>
	<tal:block define="items python:here.get_right_portlets_locations_objects(here)"
		tal:condition="python:len(items)>0">
		<tal:block tal:repeat="item items">
			<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
		</tal:block>
	</tal:block>

</div>


<tal:block tal:define="	isArabic here/isArabicLanguage;
								noArabic not:isArabic">
<div class="middle_port" tal:define="margin_string python:test(isArabic,'margin-left:0;;','margin-right:0;;')" tal:attributes="style python:test(here.getPortletsTool().get_right_portlets_locations_objects(here), '', margin_string)">
<h1>
	<img	tal:attributes="src python:test(here.approved, here.icon, here.icon_marked);
							title python:test(hasattr(here, 'meta_label'), here.meta_label, here.meta_type);
							alt python:test(hasattr(here, 'meta_label'), here.meta_label, here.meta_type)" border="0" />
	<tal:block tal:replace="here/title_or_id" />
	<tal:block tal:condition="here/can_be_seen">
		<tal:block tal:condition="here/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h1>
<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<span tal:replace="structure here/menusubmissions" />

<div tal:condition="python:btn_select or btn_delete or btn_copy or btn_cut or btn_paste">
	<div id="toolbar">
		<tal:block tal:condition="btn_select"><a href="javascript:toggleSelect();"><span><img src="/misc_/Naaya/select_all.gif" border="0" alt="Select all" i18n:attributes="alt" /><span i18n:translate="" tal:omit-tag="">Select all</span></span></a></tal:block>
		<tal:block tal:condition="btn_copy"><a href="javascript:fCopyObjects();"><span><img src="/misc_/Naaya/copy.gif" border="0" alt="Copy" i18n:attributes="alt" /><span i18n:translate="" tal:omit-tag="">Copy</span></span></a></tal:block>
		<tal:block tal:condition="btn_cut"><a href="javascript:fCutObjects();"><span><img src="/misc_/Naaya/cut.gif" border="0" alt="Cut" i18n:attributes="alt" /><span i18n:translate="" tal:omit-tag="">Cut</span></span></a></tal:block>
		<tal:block tal:condition="btn_paste"><a href="javascript:fPasteObjects();"><span><img src="/misc_/Naaya/paste.gif" border="0" alt="Paste" i18n:attributes="alt" /><span i18n:translate="" tal:omit-tag="">Paste</span></span></a></tal:block>
		<tal:block tal:condition="btn_delete"><a href="javascript:fDeleteObjects();"><span><img src="/misc_/Naaya/delete.gif" border="0" alt="Delete" i18n:attributes="alt" /><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
	</div>
</div>

<h2 i18n:translate="">Items published on the portal</h2>

<table tal:condition="here/checkPermissionEditObject">
	<tr>
		<th style="font-weight:normal;">
			<span tal:omit-tag="" i18n:translate="">Objects published after</span>
		</th>
		<td>
				<tal:block replace="python:here.utConvertDateTimeObjToString(here.criteria_date)" />
		</td>
	</tr>
	<tr>
		<th style="font-weight:normal;">
			<span tal:omit-tag i18n:translate="">Keywords</span>
		</th>
		<td>
			<tal:block condition="here/criteria_keywords" replace="here/criteria_keywords" />
			<span tal:condition="not:here/criteria_keywords" tal:omit-tag="" i18n:translate="">[none]</span>
		</td>
	</tr>
	<tr>
		<th style="font-weight:normal;">
			<p i18n:translate="">Themes</p>
		</th>
		<td>
			<tal:block define="themes here/themes; thesaurus python:here.getPortalThesaurus(); are_themes python:themes!=['']">
			<tal:block condition="not:are_themes" repeat="item themes">
				<span tal:omit-tag="" i18n:translate="">
					No themes were selected for this thematic folder.
				</span>
			</tal:block>
			<tal:block condition="are_themes" repeat="item themes">
				<tal:block define="theme_name python:thesaurus.getThemeByID(item, here.gl_get_selected_language()).theme_name">
					<a	tal:condition	="theme_name"
						tal:content		="theme_name"
						tal:attributes	="href string:${thesaurus/getThesaurusPath}/theme_concept_html?theme_id=${item}" />
					<a	tal:condition	="not:theme_name"
						tal:attributes	="href string:${thesaurus/getThesaurusPath}/theme_concept_html?theme_id=${item}" style="font-style:italic" i18n:translate="">
						no translation available
					</a>
				</tal:block>
			</tal:block>
			</tal:block>
		</td>
	</tr>
</table>

<br />
<table	class="sortable"
		tal:define="results python:portlets_data[3];
					page_search_querystring string:skey=${skey}&rkey=${rkey};
					req_params python:here.getRequestParams(request);
					sortup_gif string:${here/getSitePath}/images/sortup.gif;
					sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
					sortdown_gif string:${here/getSitePath}/images/sortdown.gif;

					list_paging python:results[0];
					paging_start python:list_paging[0]+1;
					paging_upper python:list_paging[1];
					paging_total python:list_paging[2];
					paging_prev python:list_paging[3];
					paging_next python:list_paging[4];
					paging_current_page python:list_paging[5];
					paging_records_page python:list_paging[6];
					paging_pages python:list_paging[7];

					list_result python:results[1];
					objects_list python:list_result[2];
					objects_delete_all python:list_result[1];
					objects_select_all python:list_result[0]">
<colgroup>
	<col span="3" valign="top" />
</colgroup>
<thead>
<tr>
	<th style="width: 1%">
		<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=meta_type${rkey_param};
							title python:test(skey=='meta_type', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Type</span>
		<img tal:attributes="src python:test(skey=='meta_type', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
			 width="12" height="12" alt=""/>
		</a>
	</th>

	<th>
		<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
							title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title / Abstract</span>
		<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
			 width="12" height="12" alt=""/>
		</a>
	</th>

	<th style="width: 12%">
		<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=date${rkey_param};
							title python:test(skey=='date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Last updated</span>
		<img tal:attributes="src python:test(skey=='date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
			 width="12" height="12" alt=""/>
		</a>
	</th>
</tr>
</thead>
<tr tal:condition="not:objects_list">
	<td colspan="3">
		<span omit-tag="" i18n:translate="">No entries matching the filters of this folder.</span>
	</td>
</tr>
<tr tal:repeat="item objects_list">
		<td>
			<img	tal:attributes="src item/icon;
									alt python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type);
									title python:test(hasattr(item, 'meta_label'), item.meta_label, item.meta_type)"
					align="absmiddle" />
		</td>
		<td style="padding-bottom: 5px;">
			<div style="margin-bottom:2px;">
				<tal:block condition="python:item.meta_type in ['Naaya Folder', 'Naaya Country Folder']">
					<a tal:attributes="href item/absolute_url;title item/tooltip">
						<tal:block	define="title_or_id item/title_or_id"
									replace="title_or_id"/>
					</a>
				</tal:block>
				<tal:block condition="python:item.meta_type not in ['Naaya Folder', 'Naaya Country Folder']">
					<a tal:attributes="href item/absolute_url">
						<tal:block	define="title_or_id item/title_or_id"
										replace="structure title_or_id"/>
					</a>
				</tal:block>
			</div>
			<tal:block replace="structure item/description"/>

			<tal:block condition="python:False">
				<span tal:condition="python:item.meta_type in ['Naaya Folder', 'Naaya Country Folder']" tal:replace="structure item/tooltip"/>
				<span tal:condition="python:item.meta_type not in ['Naaya Folder', 'Naaya Country Folder']" tal:replace="structure item/description"/>
			</tal:block>
		</td>
		<td><span tal:replace="python:item.utShowDateTime(item.bobobase_modification_time())"/></td>
</tr>
<tr>
	<td colspan="3">
		<p style="background-color: #f0f0f0;">
			Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
			Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
			<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
				<span	tal:repeat="page paging_pages">
					<a	class="paging-link-off"
						tal:condition="python:paging_current_page==page"
						tal:content="python:page+1" />
					<a	tal:condition="python:paging_current_page!=page"
						tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
						tal:content="python:page+1" />
				</span>
				<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
					<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
				</span>
		</p>
	</td>
</tr>
</table>


<br />
<tal:block condition="python: can_operate or folders_list">
<h2 i18n:translate="">Specific items</h2>
<form name="objectItems" method="post" action="" style="margin:0;">
<input type="hidden" name="fld_url" tal:attributes="value fld_url" />
<table border="0" cellpadding="0" cellspacing="0" id="folderfile_list">
<colgroup>
	<col span="5" valign="top" />
</colgroup>
<tr tal:condition="can_operate">
	<th class="checkbox" style="width: 1%;" i18n:translate="" tal:condition="btn_select"></th>
	<th class="type" style="width: 1%;" i18n:translate="">Type</th>
	<th class="title-column" i18n:translate="">Title</th>
	<th class="checkin" style="width:1%" i18n:translate="">Version</th>
	<th class="edit" style="width:1%;" i18n:translate="">Edit</th>
</tr>
<tr tal:repeat="folders folders_list">
	<tal:block define="del_permission python:folders[0];
		edit_permission python:folders[1];
		version_status python:folders[2];
		copy_permission python:folders[3];
		folder python:folders[4]">
	<td class="checkbox" tal:condition="btn_select" style="width: 1%; vertical-align: top;"><input tal:condition="python:del_permission or edit_permission or copy_permission" type="checkbox" name="id" tal:attributes="value folder/id" /></td>
	<td class="type" style="width: 1%;"><img tal:attributes="src python:test(folder.approved, folder.icon, folder.icon_marked); alt python:test(hasattr(folder, 'meta_label'), folder.meta_label, folder.meta_type); title python:test(hasattr(folder, 'meta_label'), folder.meta_label, folder.meta_type)" border="0" /></td>
	<td class="title-column">
		<a tal:attributes="href folder/absolute_url" tal:content="folder/title_or_id" />
		<tal:block tal:condition="folder/can_be_seen">
			<tal:block tal:condition="folder/has_restrictions" i18n:translate="">
				[Limited access]
			</tal:block>
		</tal:block>
		<tal:block tal:condition="python:not folder.can_be_seen()" i18n:translate="">
			[Restricted access]
		</tal:block>
		<tal:block tal:condition="python:folder.is_open_for_comments() and folder.count_comments()>0">
			[<span tal:replace="folder/count_comments" />
			<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
		</tal:block>
		<tal:block condition="python:False" replace="structure folder/description" />
	</td>
	<td class="checkin" tal:condition="can_operate" i18n:translate="">n/a</td>
	<td class="edit" tal:condition="can_operate">
		<a tal:condition="edit_permission" tal:attributes="href string:${folder/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
		<tal:block tal:condition="python:not edit_permission" i18n:translate="">n/a</tal:block>
	</td>
	</tal:block>
</tr>
<tr tal:repeat="objects objects_list">
	<tal:block define="del_permission python:objects[0];
			edit_permission python:objects[1];
			version_status python:objects[2];
			copy_permission python:objects[3];
			object python:objects[4]">
	<td class="checkbox" tal:condition="btn_select" style="width: 4%; vertical-align: top;"><input tal:condition="python:del_permission or edit_permission or copy_permission" type="checkbox" name="id" tal:attributes="value object/id" /></td>
	<td class="type" style="width: 4%;"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" /></td>
	<td class="title-column">
		<a tal:attributes="href object/absolute_url" tal:content="object/title_or_id" />
		<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
			[<span tal:replace="object/count_comments" />
			<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
		</tal:block>
		<span tal:replace="structure object/description" />
	</td>
	<td class="checkin" tal:condition="can_operate">
		<tal:block tal:condition="python:version_status == 0" i18n:translate="">n/a</tal:block>
		<a tal:condition="python:version_status == 2" tal:attributes="href string:${object/absolute_url}/startVersion"><img src="misc_/Naaya/checkout" border="0" alt="Checkout - start new version" i18n:attributes="alt" /></a>
		<a tal:condition="python:version_status == 1" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/checkin" border="0" alt="Version control" i18n:attributes="alt" /></a>
	</td>
	<td class="edit" tal:condition="can_operate">
		<a tal:condition="python:edit_permission and not object.hasVersion()" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
		<tal:block tal:condition="python:edit_permission and object.hasVersion() or not edit_permission" i18n:translate="">n/a</tal:block>
	</td>
	</tal:block>
</tr>
</table>
</form>
</tal:block>
<p>
	<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>
</p>

<span tal:replace="structure here/comments_box" />

</div>
</tal:block>
</tal:block>
<span tal:replace="structure here/standard_html_footer"/>
"""
        semide_nfp_private_agenda_index = """<span tal:replace="structure here/standard_html_header" />
<div class="middle_port" style='margin-right:0;'>

<tal:block	define="sq python:request.get('sq', '');
					sl python:here.utConvertToList(request.get('sl', []));
					et python:request.get('et', '');
					gz python:request.get('gz', '');
					es python:request.get('es', '');
					sd python:request.get('sd', '');
					ed python:request.get('ed', '');
					ps_start python:request.get('start', 0);
					skey python:request.get('skey', 'start_date');
					rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
					rkey_param python:test(rkey, '', '&amp;rkey=1');

					page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&et=${et}&gz=${gz}&es=${es}&sd=${sd}&ed=${ed};
					results python:here.getEventsNFP(sq, sl, et, gz, es, skey, rkey, sd, ed, here.absolute_url(1), ps_start);

					list_paging python:results[0];
					paging_start python:list_paging[0]+1;
					paging_upper python:list_paging[1];
					paging_total python:list_paging[2];
					paging_prev python:list_paging[3];
					paging_next python:list_paging[4];
					paging_current_page python:list_paging[5];
					paging_records_page python:list_paging[6];
					paging_pages python:list_paging[7];

					list_result python:results[1];
					objects_list python:list_result[2];
					objects_delete_all python:list_result[1];
					objects_select_all python:list_result[0]">

<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
<!--
	function fCheckSelection()
	{	var frm = document.objectItems;
	var i;
	check = false;
	for(i=0; i<frm.elements.length; i++)
		if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
		{	check = true; break;}
		return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
<!--
	function fDeleteObjects()
	{	if (fCheckSelection())
	{	document.objectItems.action="deleteObjects";
	document.objectItems.submit();}
	else
	alert('Please select one or more items to delete.');}
//-->
</script>

<div id="right_port">
	<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<h2 tal:define="l_parent python:here.aq_parent">
	<img tal:attributes="src python:test(l_parent.approved, l_parent.icon, l_parent.icon_marked); title l_parent/meta_label; alt l_parent/meta_label" border="0" />
	<tal:block tal:replace="l_parent/title_or_id" />
	<tal:block tal:condition="l_parent/can_be_seen">
		<tal:block tal:condition="l_parent/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not l_parent.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h2>

<h1>
	<tal:block tal:replace="here/title_or_id" />
	<tal:block tal:condition="here/can_be_seen">
		<tal:block tal:condition="here/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h1>

<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<tal:block	tal:define="this_absolute_url python:here.absolute_url(0);
						submissions here/process_submissions;
						perm_add_something python:len(submissions)>0;
						perm_edit_object here/checkPermissionEditObject;
						perm_publish_objects here/checkPermissionPublishObjects">
<div id="admin_this_folder" tal:condition="python:perm_edit_object and perm_publish_objects">
	<span id="submission" tal:condition="perm_add_something">
		<span i18n:translate="" tal:omit-tag="">Submit</span>:
		<select name="typetoadd"
			tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
			<option value="#" i18n:translate="">Type to add</option>
			<option tal:repeat="item submissions"
				tal:attributes="value python:item[0]"
				tal:content="python:item[1]" i18n:translate="" />
		</select>
	</span>
	<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
		<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
	</tal:block>
</div>
</tal:block>

<fieldset class="search_field"><legend i18n:translate="">Search events</legend>
<div class="fieldset_div">
<form method="get" action="">
<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
<div class="field">
	<label for="sq" i18n:translate="">Query</label>
	<input type="text" name="sq" id="sq" size="50" tal:attributes="value sq" />
</div>
<div class="field">
	<label for="et" i18n:translate="">Type</label>
	<select name="et" id="et">
		<option value=""></option>
		<option tal:repeat="item here/getEventTypesList"
			tal:attributes="value item/id; selected python:item.id==et" tal:content="item/title" i18n:translate="" />
	</select>
</div>
<div class="field">
	<label for="es" i18n:translate="">Status</label>
	<select name="es" id="es">
		<option value=""></option>
		<option tal:repeat="item here/getEventStatusList"
			tal:attributes="value item/id; selected python:item.id==es" tal:content="item/title" i18n:translate="" />
	</select>
</div>
<div class="field">
	<label for="gz" i18n:translate="">Location</label>
	<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
		<option value="" />
		<tal:block repeat="item langs_list">
			<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
								translation python:item.get_translation_by_language(lang_name)">
				<option	tal:condition="translation"
						tal:attributes="value item/id; selected python:item.id == gz"
						tal:content="translation" />
				<tal:block	condition="not:translation"
							define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
									def_trans python:item.get_translation_by_language(lang_name)">
					<option	tal:condition="def_trans"
							tal:attributes="value item/id; selected python:item.id == gz"
							tal:content="def_trans" />
					<option	tal:condition="not:def_trans"
							tal:attributes="value item/id; selected python:item.id == gz"
							i18n:translate="">no translation available</option>
				</tal:block>
			</tal:block>
		</tal:block>
	</select>
</div>
<div class="clear_float"></div>
<div class="field" style="margin-top:10px;">
	<span>Start date between:</span>
	<input type="text" name="sd" id="sd" size="10" tal:attributes="value sd" /> and <input type="text" name="ed" id="es" size="10" tal:attributes="value ed" />
	<span>dd/mm/yyyy</span>
	<input type="submit" value="Search" i18n:attributes="value" />
</div>
<div class="clear_float"></div>
</form>
</div>
</fieldset>


<h2>
	<span tal:condition="python:sq=='' and sl==[] and et=='' and gz=='' and es=='' and sd=='' and ed==''" i18n:translate="">Upcoming events</span>
	<span tal:condition="python:not(sq=='' and sl==[] and et=='' and gz=='' and es=='' and sd=='' and ed=='')" i18n:translate="">Search results</span>
</h2>

<div tal:condition="python:objects_select_all or objects_delete_all">
	<div id="toolbar">
		<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
	</div>
</div>

<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No events available</p>
<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
		tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
					sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
					sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
					req_params python:here.getRequestParams(request)">
	<tr>
		<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
		<th style="width: 10%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
								title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
			<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
								title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
			<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th style="width: 15%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
								title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Location</span>
			<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=source${rkey_param};
								title python:test(skey=='source', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Source</span>
			<img tal:attributes="src python:test(skey=='source', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th><span i18n:translate="" title="not sortable">Link</span></th>
		<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
	</tr>
	<tr tal:repeat="objects objects_list">
		<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
			<td class="checkbox" tal:condition="del_permission" width="4%" valign="top"><input type="checkbox" name="id" tal:attributes="value object/id" /></td>
			<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
			<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
			<a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
				<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
					[<span tal:replace="object/count_comments" />
					<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
				</tal:block>
			</td>
			<td tal:content="python:test(object.coverage, object.coverage, '-')" />
			<td tal:content="python:test(object.source, object.source, '-')" />
			<td><a tal:condition="python:object.file_link not in ['', 'http://']" tal:attributes="href python:test(object.file_link, object.file_link, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.file_link in ['', 'http://']">-</span></td>
			<td class="edit" tal:condition="edit_permission">
				<a tal:condition="python:not object.hasVersion()" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
			</td>
		</tal:block>
	</tr>
</table>
</form>

<p>
	Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
	Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
	<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
		tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
		<span	tal:repeat="page paging_pages">
			<a	class="paging-link-off"
				tal:condition="python:paging_current_page==page"
				tal:content="python:page+1" />
			<a	tal:condition="python:paging_current_page!=page"
				tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
				tal:content="python:page+1" />
		</span>
		<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
			<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
		</span>
</p>
</tal:block>

<p>
	<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

	<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
	<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
	</tal:block>
</p>

<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
	[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
</p>
</div>
<span tal:replace="structure here/standard_html_footer"/>
"""

        semide_initiative_database_index = """<span tal:replace="structure here/standard_html_header" />
<div id="middle_port" style='margin-right:0;'>

<tal:block	define="sq python:request.get('sq', '');
					so python:request.get('so', '');
					gz python:request.get('gz', '');
					th python:request.get('th', '');
					pr python:request.get('pr', '');
					sel_lang python:here.gl_get_selected_language();
					sl python:here.utConvertToList(request.get('sl', [sel_lang]));
					ps_start python:request.get('start', 0);
					archive python:here.getObjects();
					skey python:request.get('skey', 'start_date');
					rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
					rkey_param python:test(rkey, '', '&amp;rkey=1');

					langs_querystring python:'&sl:list='.join(sl);
					page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&so=${so}&sl:list=${langs_querystring}&gz=${gz}&th=${th}&pr=${pr};
					results python:here.getProjectsListing(sq, so, sl, skey, rkey, archive, ps_start, gz, th, pr);

					list_paging python:results[0];
					paging_start python:list_paging[0]+1;
					paging_upper python:list_paging[1];
					paging_total python:list_paging[2];
					paging_prev python:list_paging[3];
					paging_next python:list_paging[4];
					paging_current_page python:list_paging[5];
					paging_records_page python:list_paging[6];
					paging_pages python:list_paging[7];

					list_result python:results[1];
					objects_list python:list_result[2];
					objects_delete_all python:list_result[1];
					objects_select_all python:list_result[0]">

<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
<!--
	function fCheckSelection()
	{	var frm = document.objectItems;
	var i;
	check = false;
	for(i=0; i<frm.elements.length; i++)
		if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
		{	check = true; break;}
		return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
<!--
	function fDeleteObjects()
	{	if (fCheckSelection())
	{	document.objectItems.action="deleteObjects";
	document.objectItems.submit();}
	else
	alert('Please select one or more items to delete.');}
//-->
</script>

<div id="right_port">
	<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<h1>
	<tal:block tal:replace="here/title_or_id" />
	<tal:block tal:condition="here/can_be_seen">
		<tal:block tal:condition="here/has_restrictions" i18n:translate="">
			[Limited access]
		</tal:block>
	</tal:block>
	<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
		[Restricted access]
	</tal:block>
</h1>

<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<tal:block	tal:define="this_absolute_url python:here.absolute_url(0);
						submissions here/process_submissions;
						perm_add_something python:len(submissions)>0;
						perm_edit_object here/checkPermissionEditObject;
						perm_publish_objects here/checkPermissionPublishObjects">
<div id="admin_this_folder" tal:condition="python:perm_add_something or perm_edit_object and perm_publish_objects">
	<span id="submission" tal:condition="perm_add_something">
		<span i18n:translate="" tal:omit-tag="">Submit</span>:
		<select name="typetoadd"
			tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
			<option value="#" i18n:translate="">Type to add</option>
			<option tal:repeat="item submissions"
				tal:attributes="value python:item[0]"
				tal:content="python:item[1]" i18n:translate="" />
		</select>
	</span>
	<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
		<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
	</tal:block>
</div>
</tal:block>

<fieldset class="search_field"><legend i18n:translate="">Search projects</legend>
	<div class="fieldset_div">
		<form method="get" action="">
			<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
			<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
			<div class="field">
				<label for="sq" i18n:translate="">Query</label>
				<input type="text" name="sq" id="sq" size="30" tal:attributes="value sq" />
			</div>
			<div class="field">
				<label for="pr" i18n:translate="">Programme</label>
				<input type="text" name="pr" id="pr" size="30" tal:attributes="value pr" />
			</div>
			<div class="field">
				<label for="so" i18n:translate="">Organisation</label>
				<input type="text" name="so" id="so" size="30" tal:attributes="value so" />
			</div>
			<div class="field">
				<label for="th" i18n:translate="">Theme</label>
				<select name="th" id="th">
					<option value="" />
					<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(here.gl_get_selected_language())">
						<option	tal:condition="item/theme_name"
								tal:attributes="value item/theme_id;
												selected python:item.theme_id == th"
								tal:content="item/theme_name" />
						<option	tal:condition="not:item/theme_name"
								tal:attributes="value item/theme_id;
												selected python:item.theme_id == th"
								i18n:translate="">no translation available</option>
					</tal:block>
				</select>
			</div>
			<div class="field">
				<label for="gz" i18n:translate="">Country</label>
				<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
					<option value="" />
					<tal:block repeat="item langs_list">
						<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
											translation python:item.get_translation_by_language(lang_name)">
							<option	tal:condition="translation"
									tal:attributes="value item/id; selected python:item.id == gz"
									tal:content="translation" />
							<tal:block	condition="not:translation"
										define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
												def_trans python:item.get_translation_by_language(lang_name)">
								<option	tal:condition="def_trans"
										tal:attributes="value item/id; selected python:item.id == gz"
										tal:content="def_trans" />
								<option	tal:condition="not:def_trans"
										tal:attributes="value item/id; selected python:item.id == gz"
										i18n:translate="">no translation available</option>
							</tal:block>
						</tal:block>
					</tal:block>
				</select>
			</div>
			<div class="field">
				<br />
				<input type="submit" value="Search" i18n:attributes="value" />
			</div>
			<div class="clear_float"></div>
			<div class="field-inline" tal:define="selected_language here/gl_get_selected_language">
				<strong i18n:translate="">Languages: </strong>
				<tal:block repeat="item here/gl_get_languages_mapping">
					<input	name="sl" type="checkbox"
							tal:attributes="value python:item['code'];
											checked python:item['code'] in sl;
											id python:'sl_'+item['code']" />
					<label class="search_language" tal:attributes="for python:'sl_'+item['code']" tal:content="python:item['name']" />
				</tal:block>
			</div>
		</form>
	</div>
</fieldset>

<h2>
	<span tal:condition="python:sq=='' and so=='' and th=='' and gz=='' and pr==''" i18n:translate="">Projects</span>
	<span tal:condition="python:not(sq=='' and so=='' and th=='' and gz=='' and pr=='')" i18n:translate="">Search results</span>
</h2>

<div tal:condition="python:objects_select_all or objects_delete_all">
	<div id="toolbar">
		<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
	</div>
</div>

<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No projects available</p>
<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
		tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
					sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
					sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
					req_params python:here.getRequestParams(request)">
	<tr>
		<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
		<th style="width: 10%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
								title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
			<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
								title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
			<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th style="width: 15%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
								title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Countries</span>
			<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=programme${rkey_param};
								title python:test(skey=='programme', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Programme</span>
			<img tal:attributes="src python:test(skey=='programme', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th><span i18n:translate="" title="not sortable">Link</span></th>
		<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable" i18n:attributes="title">Edit</span></th>
	</tr>
	<tr tal:repeat="objects objects_list">
		<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
			<td class="checkbox" tal:condition="del_permission" width="4%" valign="top">
				<input tal:condition="python:object in archive" type="checkbox" name="id" tal:attributes="value object/id" />
				<span tal:condition="python:not object in archive">-</span>
			</td>
			<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
			<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
			<a tal:attributes="href object/absolute_url;title python:here.stripAllHtmlTags(object.description)" tal:content="object/title_or_id" />
				<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
					[<span tal:replace="object/count_comments" />
					<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
				</tal:block>
			</td>
			<td tal:content="python:test(object.coverage, object.coverage, '-')" />
			<td tal:content="python:test(object.programme, object.programme, '-')" />
			<td><a tal:condition="python:object.resourceurl not in ['', 'http://']" tal:attributes="href python:test(object.resourceurl, object.resourceurl, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.resourceurl in ['', 'http://']">-</span></td>
			<td class="edit" tal:condition="edit_permission">
				<a tal:condition="python:not object.hasVersion() and object in archive" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
				<span tal:condition="python:not(not object.hasVersion() and object in archive)">-</span>
			</td>
		</tal:block>
	</tr>
</table>
</form>

<p>
	Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
	Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
	<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
		tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
		<span	tal:repeat="page paging_pages">
			<a	class="paging-link-off"
				tal:condition="python:paging_current_page==page"
				tal:content="python:page+1" />
			<a	tal:condition="python:paging_current_page!=page"
				tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
				tal:content="python:page+1" />
		</span>
		<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
			<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
		</span>
</p>
</tal:block>

<p>
	<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

	<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
	<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
	</tal:block>
</p>

<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
	[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
</p>
</div>
<span tal:replace="structure here/standard_html_footer"/>
"""

        semide_initiatives_medaeau_projects = """<span tal:replace="structure here/standard_html_header" />

	<tal:block	define="sq python:request.get('sq', '');
						so python:request.get('so', '');
						gz python:request.get('gz', '');
						th python:request.get('th', '');
						pr python:request.get('pr', '');
						sel_lang python:here.gl_get_selected_language();
						sl python:here.utConvertToList(request.get('sl', [sel_lang]));
						ps_start python:request.get('start', 0);
						archive python:here.getObjects();
						skey python:request.get('skey', 'start_date');
						rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
						rkey_param python:test(rkey, '', '&amp;rkey=1');

						langs_querystring python:'&sl:list='.join(sl);
						page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&so=${so}&sl:list=${langs_querystring}&gz=${gz}&th=${th}&pr=${pr};
						results python:here.getProjectsListing(sq, so, sl, skey, rkey, archive, ps_start, gz, th, pr);

						list_paging python:results[0];
						paging_start python:list_paging[0]+1;
						paging_upper python:list_paging[1];
						paging_total python:list_paging[2];
						paging_prev python:list_paging[3];
						paging_next python:list_paging[4];
						paging_current_page python:list_paging[5];
						paging_records_page python:list_paging[6];
						paging_pages python:list_paging[7];

						list_result python:results[1];
						objects_list python:list_result[2];
						objects_delete_all python:list_result[1];
						objects_select_all python:list_result[0]">

	<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
	<!--
		function fCheckSelection()
		{	var frm = document.objectItems;
		var i;
		check = false;
		for(i=0; i<frm.elements.length; i++)
			if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
			{	check = true; break;}
			return check;}
	//-->
	</script>

	<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
	<!--
		function fDeleteObjects()
		{	if (fCheckSelection())
		{	document.objectItems.action="deleteObjects";
		document.objectItems.submit();}
		else
		alert('Please select one or more items to delete.');}
	//-->
	</script>

	<div id="right_port">
		<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
			<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
		</tal:block>
	</div>

	<div class="middle_port">
		<h1>
			<tal:block tal:replace="here/title_or_id" />
			<tal:block tal:condition="here/can_be_seen">
				<tal:block tal:condition="here/has_restrictions" i18n:translate="">
					[Limited access]
				</tal:block>
			</tal:block>
			<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
				[Restricted access]
			</tal:block>
		</h1>

		<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

		<tal:block	tal:define="this_absolute_url python:here.absolute_url(0);
								submissions here/process_submissions;
								perm_add_something python:len(submissions)>0;
								perm_edit_object here/checkPermissionEditObject;
								perm_publish_objects here/checkPermissionPublishObjects">
			<div id="admin_this_folder" tal:condition="python:perm_edit_object and perm_publish_objects">
				<span id="submission" tal:condition="perm_add_something">
					<span i18n:translate="" tal:omit-tag="">Submit</span>:
					<select name="typetoadd"
						tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
						<option value="#" i18n:translate="">Type to add</option>
						<option tal:repeat="item submissions"
							tal:attributes="value python:item[0]"
							tal:content="python:item[1]" i18n:translate="" />
					</select>
				</span>
				<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
					<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
					<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
				</tal:block>
			</div>
		</tal:block>

		<fieldset class="search_field"><legend i18n:translate="">Search projects</legend>
			<div class="fieldset_div">
				<form method="get" action="">
					<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
					<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
					<div class="field">
						<label for="sq" i18n:translate="">Query</label>
						<input type="text" name="sq" id="sq" size="30" tal:attributes="value sq" />
					</div>
					<div class="field">
						<label for="pr" i18n:translate="">Programme</label>
						<input type="text" name="pr" id="pr" size="30" tal:attributes="value pr" />
					</div>
					<div class="field">
						<label for="so" i18n:translate="">Organisation</label>
						<input type="text" name="so" id="so" size="30" tal:attributes="value so" />
						<input type="submit" value="Search" i18n:attributes="value" />
					</div>
					<div class="field">
						<label for="th" i18n:translate="">Theme</label>
						<select name="th" id="th">
							<option value="" />
							<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(here.gl_get_selected_language())">
								<option	tal:condition="item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										tal:content="item/theme_name" />
								<option	tal:condition="not:item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										i18n:translate="">no translation available</option>
							</tal:block>
						</select>
					</div>
					<div class="field">
						<label for="gz" i18n:translate="">Country</label>
						<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
							<option value="" />
							<tal:block repeat="item langs_list">
								<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
													translation python:item.get_translation_by_language(lang_name)">
									<option	tal:condition="translation"
											tal:attributes="value item/id; selected python:item.id == gz"
											tal:content="translation" />
									<tal:block	condition="not:translation"
												define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
														def_trans python:item.get_translation_by_language(lang_name)">
										<option	tal:condition="def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												tal:content="def_trans" />
										<option	tal:condition="not:def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												i18n:translate="">no translation available</option>
									</tal:block>
								</tal:block>
							</tal:block>
						</select>
					</div>
					<div class="clear_float"></div>
					<div class="field-inline" tal:define="selected_language here/gl_get_selected_language">
						<strong i18n:translate="">Languages: </strong>
						<tal:block repeat="item here/gl_get_languages_mapping">
						<input name="sl" type="checkbox"
							tal:attributes="value python:item['code']; checked python:item['code'] in sl; id python:'sl_'+item['code']"
							/><label class="search_language" tal:attributes="for python:'sl_'+item['code']" tal:content="python:item['name']" />
						</tal:block>
					</div>
				</form>
			</div>
		</fieldset>

		<br />

		<h2>
			<span tal:condition="python:sq=='' and so=='' and th=='' and gz=='' and pr==''" i18n:translate="">Projects</span>
			<span tal:condition="python:not(sq=='' and so=='' and th=='' and gz=='' and pr=='')" i18n:translate="">Search results</span>
		</h2>

		<div tal:condition="python:objects_select_all or objects_delete_all">
			<div id="toolbar">
				<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
			</div>
		</div>

		<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No projects available</p>
		<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
		<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
				tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
							sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
							sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
							req_params python:here.getRequestParams(request)">
			<tr>
				<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
				<th style="width: 10%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
										title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
					<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
										title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
					<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th style="width: 15%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
										title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Countries</span>
					<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=programme${rkey_param};
										title python:test(skey=='programme', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Programme</span>
					<img tal:attributes="src python:test(skey=='programme', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th><span i18n:translate="" title="not sortable">Link</span></th>
				<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
			</tr>
			<tr tal:repeat="objects objects_list">
				<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
					<td class="checkbox" tal:condition="del_permission" width="4%" valign="top">
						<input tal:condition="python:object in archive" type="checkbox" name="id" tal:attributes="value object/id" />
						<span tal:condition="python:not object in archive">-</span>
					</td>
					<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
					<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
					<a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
						<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
							[<span tal:replace="object/count_comments" />
							<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
						</tal:block>
					</td>
					<td tal:content="python:test(object.coverage, object.coverage, '-')" />
					<td tal:content="python:test(object.programme, object.programme, '-')" />
					<td><a tal:condition="python:object.resourceurl not in ['', 'http://']" tal:attributes="href python:test(object.resourceurl, object.resourceurl, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.resourceurl in ['', 'http://']">-</span></td>
					<td class="edit" tal:condition="edit_permission">
						<a tal:condition="python:not object.hasVersion() and object in archive" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
						<span tal:condition="python:not(not object.hasVersion() and object in archive)">-</span>
					</td>
				</tal:block>
			</tr>
		</table>
		</form>

		<p>
			Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
			Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
			<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
				<span	tal:repeat="page paging_pages">
					<a	class="paging-link-off"
						tal:condition="python:paging_current_page==page"
						tal:content="python:page+1" />
					<a	tal:condition="python:paging_current_page!=page"
						tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
						tal:content="python:page+1" />
				</span>
				<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
					<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
				</span>
		</p>
	</div>
	</tal:block>
	<p>
		<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

		<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
		<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
		</tal:block>
	</p>

	<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
		[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
	</p>
<span tal:replace="structure here/standard_html_footer"/>
"""

        semide_initiatives_incomed_projects = """<span tal:replace="structure here/standard_html_header" />

	<tal:block	define="sq python:request.get('sq', '');
						so python:request.get('so', '');
						gz python:request.get('gz', '');
						th python:request.get('th', '');
						pr python:request.get('pr', '');
						sel_lang python:here.gl_get_selected_language();
						sl python:here.utConvertToList(request.get('sl', [sel_lang]));
						ps_start python:request.get('start', 0);
						archive python:here.getObjects();
						skey python:request.get('skey', 'start_date');
						rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
						rkey_param python:test(rkey, '', '&amp;rkey=1');

						langs_querystring python:'&sl:list='.join(sl);
						page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&so=${so}&sl:list=${langs_querystring}&gz=${gz}&th=${th}&pr=${pr};
						results python:here.getProjectsListing(sq, so, sl, skey, rkey, archive, ps_start, gz, th, pr);

						list_paging python:results[0];
						paging_start python:list_paging[0]+1;
						paging_upper python:list_paging[1];
						paging_total python:list_paging[2];
						paging_prev python:list_paging[3];
						paging_next python:list_paging[4];
						paging_current_page python:list_paging[5];
						paging_records_page python:list_paging[6];
						paging_pages python:list_paging[7];

						list_result python:results[1];
						objects_list python:list_result[2];
						objects_delete_all python:list_result[1];
						objects_select_all python:list_result[0]">

	<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
	<!--
		function fCheckSelection()
		{	var frm = document.objectItems;
		var i;
		check = false;
		for(i=0; i<frm.elements.length; i++)
			if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
			{	check = true; break;}
			return check;}
	//-->
	</script>

	<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
	<!--
		function fDeleteObjects()
		{	if (fCheckSelection())
		{	document.objectItems.action="deleteObjects";
		document.objectItems.submit();}
		else
		alert('Please select one or more items to delete.');}
	//-->
	</script>

	<div id="right_port">
		<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
			<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
		</tal:block>
	</div>

	<div class="middle_port">
		<h1>
			<tal:block tal:replace="here/title_or_id" />
			<tal:block tal:condition="here/can_be_seen">
				<tal:block tal:condition="here/has_restrictions" i18n:translate="">
					[Limited access]
				</tal:block>
			</tal:block>
			<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
				[Restricted access]
			</tal:block>
		</h1>

		<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

		<tal:block	tal:define="this_absolute_url python:here.absolute_url(0);
								submissions here/process_submissions;
								perm_add_something python:len(submissions)>0;
								perm_edit_object here/checkPermissionEditObject;
								perm_publish_objects here/checkPermissionPublishObjects">
			<div id="admin_this_folder" tal:condition="python:perm_edit_object and perm_publish_objects">
				<span id="submission" tal:condition="perm_add_something">
					<span i18n:translate="" tal:omit-tag="">Submit</span>:
					<select name="typetoadd"
						tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
						<option value="#" i18n:translate="">Type to add</option>
						<option tal:repeat="item submissions"
							tal:attributes="value python:item[0]"
							tal:content="python:item[1]" i18n:translate="" />
					</select>
				</span>
				<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
					<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
					<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
				</tal:block>
			</div>
		</tal:block>

		<fieldset class="search_field"><legend i18n:translate="">Search projects</legend>
			<div class="fieldset_div">
				<form method="get" action="">
					<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
					<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
					<div class="field">
						<label for="sq" i18n:translate="">Query</label>
						<input type="text" name="sq" id="sq" size="30" tal:attributes="value sq" />
					</div>
					<div class="field">
						<label for="pr" i18n:translate="">Programme</label>
						<input type="text" name="pr" id="pr" size="30" tal:attributes="value pr" />
					</div>
					<div class="field">
						<label for="so" i18n:translate="">Organisation</label>
						<input type="text" name="so" id="so" size="30" tal:attributes="value so" />
						<input type="submit" value="Search" i18n:attributes="value" />
					</div>
					<div class="field">
						<label for="th" i18n:translate="">Theme</label>
						<select name="th" id="th">
							<option value="" />
							<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(here.gl_get_selected_language())">
								<option	tal:condition="item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										tal:content="item/theme_name" />
								<option	tal:condition="not:item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										i18n:translate="">no translation available</option>
							</tal:block>
						</select>
					</div>
					<div class="field">
						<label for="gz" i18n:translate="">Country</label>
						<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
							<option value="" />
							<tal:block repeat="item langs_list">
								<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
													translation python:item.get_translation_by_language(lang_name)">
									<option	tal:condition="translation"
											tal:attributes="value item/id; selected python:item.id == gz"
											tal:content="translation" />
									<tal:block	condition="not:translation"
												define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
														def_trans python:item.get_translation_by_language(lang_name)">
										<option	tal:condition="def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												tal:content="def_trans" />
										<option	tal:condition="not:def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												i18n:translate="">no translation available</option>
									</tal:block>
								</tal:block>
							</tal:block>
						</select>
					</div>
					<div class="clear_float"></div>
					<div class="field-inline" tal:define="selected_language here/gl_get_selected_language">
						<strong i18n:translate="">Languages: </strong>
						<tal:block repeat="item here/gl_get_languages_mapping">
						<input name="sl" type="checkbox"
							tal:attributes="value python:item['code']; checked python:item['code'] in sl; id python:'sl_'+item['code']"
							/><label class="search_language" tal:attributes="for python:'sl_'+item['code']" tal:content="python:item['name']" />
						</tal:block>
					</div>
				</form>
			</div>
		</fieldset>

		<br />

		<h2>
			<span tal:condition="python:sq=='' and so=='' and th=='' and gz=='' and pr==''" i18n:translate="">Projects</span>
			<span tal:condition="python:not(sq=='' and so=='' and th=='' and gz=='' and pr=='')" i18n:translate="">Search results</span>
		</h2>

		<div tal:condition="python:objects_select_all or objects_delete_all">
			<div id="toolbar">
				<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
			</div>
		</div>

		<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No projects available</p>
		<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
		<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
				tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
							sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
							sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
							req_params python:here.getRequestParams(request)">
			<tr>
				<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
				<th style="width: 10%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
										title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
					<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
										title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
					<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th style="width: 15%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
										title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Countries</span>
					<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=programme${rkey_param};
										title python:test(skey=='programme', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Programme</span>
					<img tal:attributes="src python:test(skey=='programme', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th><span i18n:translate="" title="not sortable">Link</span></th>
				<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
			</tr>
			<tr tal:repeat="objects objects_list">
				<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
					<td class="checkbox" tal:condition="del_permission" width="4%" valign="top">
						<input tal:condition="python:object in archive" type="checkbox" name="id" tal:attributes="value object/id" />
						<span tal:condition="python:not object in archive">-</span>
					</td>
					<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
					<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
					<a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
						<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
							[<span tal:replace="object/count_comments" />
							<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
						</tal:block>
					</td>
					<td tal:content="python:test(object.coverage, object.coverage, '-')" />
					<td tal:content="python:test(object.programme, object.programme, '-')" />
					<td><a tal:condition="python:object.resourceurl not in ['', 'http://']" tal:attributes="href python:test(object.resourceurl, object.resourceurl, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.resourceurl in ['', 'http://']">-</span></td>
					<td class="edit" tal:condition="edit_permission">
						<a tal:condition="python:not object.hasVersion() and object in archive" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
						<span tal:condition="python:not(not object.hasVersion() and object in archive)">-</span>
					</td>
				</tal:block>
			</tr>
		</table>
		</form>

		<p>
			Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
			Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
			<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
				<span	tal:repeat="page paging_pages">
					<a	class="paging-link-off"
						tal:condition="python:paging_current_page==page"
						tal:content="python:page+1" />
					<a	tal:condition="python:paging_current_page!=page"
						tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
						tal:content="python:page+1" />
				</span>
				<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
					<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
				</span>
		</p>
	</div>
	</tal:block>
	<p>
		<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

		<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
		<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
		</tal:block>
	</p>

	<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
		[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
	</p>
<span tal:replace="structure here/standard_html_footer"/>
"""
        semide_initiatives_life_projects = """<span tal:replace="structure here/standard_html_header" />

	<tal:block	define="sq python:request.get('sq', '');
						so python:request.get('so', '');
						gz python:request.get('gz', '');
						th python:request.get('th', '');
						pr python:request.get('pr', '');
						sel_lang python:here.gl_get_selected_language();
						sl python:here.utConvertToList(request.get('sl', [sel_lang]));
						ps_start python:request.get('start', 0);
						archive python:here.getObjects();
						skey python:request.get('skey', 'start_date');
						rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
						rkey_param python:test(rkey, '', '&amp;rkey=1');

						langs_querystring python:'&sl:list='.join(sl);
						page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&so=${so}&sl:list=${langs_querystring}&gz=${gz}&th=${th}&pr=${pr};
						results python:here.getProjectsListing(sq, so, sl, skey, rkey, archive, ps_start, gz, th, pr);

						list_paging python:results[0];
						paging_start python:list_paging[0]+1;
						paging_upper python:list_paging[1];
						paging_total python:list_paging[2];
						paging_prev python:list_paging[3];
						paging_next python:list_paging[4];
						paging_current_page python:list_paging[5];
						paging_records_page python:list_paging[6];
						paging_pages python:list_paging[7];

						list_result python:results[1];
						objects_list python:list_result[2];
						objects_delete_all python:list_result[1];
						objects_select_all python:list_result[0]">

	<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
	<!--
		function fCheckSelection()
		{	var frm = document.objectItems;
		var i;
		check = false;
		for(i=0; i<frm.elements.length; i++)
			if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
			{	check = true; break;}
			return check;}
	//-->
	</script>

	<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
	<!--
		function fDeleteObjects()
		{	if (fCheckSelection())
		{	document.objectItems.action="deleteObjects";
		document.objectItems.submit();}
		else
		alert('Please select one or more items to delete.');}
	//-->
	</script>

	<div id="right_port">
		<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
			<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
		</tal:block>
	</div>

	<div class="middle_port">
		<h1>
			<tal:block tal:replace="here/title_or_id" />
			<tal:block tal:condition="here/can_be_seen">
				<tal:block tal:condition="here/has_restrictions" i18n:translate="">
					[Limited access]
				</tal:block>
			</tal:block>
			<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
				[Restricted access]
			</tal:block>
		</h1>

		<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

		<tal:block	tal:define="this_absolute_url python:here.absolute_url(0);
								submissions here/process_submissions;
								perm_add_something python:len(submissions)>0;
								perm_edit_object here/checkPermissionEditObject;
								perm_publish_objects here/checkPermissionPublishObjects">
			<div id="admin_this_folder" tal:condition="python:perm_edit_object and perm_publish_objects">
				<span id="submission" tal:condition="perm_add_something">
					<span i18n:translate="" tal:omit-tag="">Submit</span>:
					<select name="typetoadd"
						tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
						<option value="#" i18n:translate="">Type to add</option>
						<option tal:repeat="item submissions"
							tal:attributes="value python:item[0]"
							tal:content="python:item[1]" i18n:translate="" />
					</select>
				</span>
				<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
					<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
					<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
				</tal:block>
			</div>
		</tal:block>

		<fieldset class="search_field"><legend i18n:translate="">Search projects</legend>
			<div class="fieldset_div">
				<form method="get" action="">
					<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
					<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
					<div class="field">
						<label for="sq" i18n:translate="">Query</label>
						<input type="text" name="sq" id="sq" size="30" tal:attributes="value sq" />
					</div>
					<div class="field">
						<label for="pr" i18n:translate="">Programme</label>
						<input type="text" name="pr" id="pr" size="30" tal:attributes="value pr" />
					</div>
					<div class="field">
						<label for="so" i18n:translate="">Organisation</label>
						<input type="text" name="so" id="so" size="30" tal:attributes="value so" />
						<input type="submit" value="Search" i18n:attributes="value" />
					</div>
					<div class="field">
						<label for="th" i18n:translate="">Theme</label>
						<select name="th" id="th">
							<option value="" />
							<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(here.gl_get_selected_language())">
								<option	tal:condition="item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										tal:content="item/theme_name" />
								<option	tal:condition="not:item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										i18n:translate="">no translation available</option>
							</tal:block>
						</select>
					</div>
					<div class="field">
						<label for="gz" i18n:translate="">Country</label>
						<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
							<option value="" />
							<tal:block repeat="item langs_list">
								<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
													translation python:item.get_translation_by_language(lang_name)">
									<option	tal:condition="translation"
											tal:attributes="value item/id; selected python:item.id == gz"
											tal:content="translation" />
									<tal:block	condition="not:translation"
												define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
														def_trans python:item.get_translation_by_language(lang_name)">
										<option	tal:condition="def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												tal:content="def_trans" />
										<option	tal:condition="not:def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												i18n:translate="">no translation available</option>
									</tal:block>
								</tal:block>
							</tal:block>
						</select>
					</div>
					<div class="clear_float"></div>
					<div class="field-inline" tal:define="selected_language here/gl_get_selected_language">
						<strong i18n:translate="">Languages: </strong>
						<tal:block repeat="item here/gl_get_languages_mapping">
						<input name="sl" type="checkbox"
							tal:attributes="value python:item['code']; checked python:item['code'] in sl; id python:'sl_'+item['code']"
							/><label class="search_language" tal:attributes="for python:'sl_'+item['code']" tal:content="python:item['name']" />
						</tal:block>
					</div>
				</form>
			</div>
		</fieldset>

		<br />

		<h2>
			<span tal:condition="python:sq=='' and so=='' and th=='' and gz=='' and pr==''" i18n:translate="">Projects</span>
			<span tal:condition="python:not(sq=='' and so=='' and th=='' and gz=='' and pr=='')" i18n:translate="">Search results</span>
		</h2>

		<div tal:condition="python:objects_select_all or objects_delete_all">
			<div id="toolbar">
				<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
			</div>
		</div>

		<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No projects available</p>
		<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
		<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
				tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
							sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
							sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
							req_params python:here.getRequestParams(request)">
			<tr>
				<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
				<th style="width: 10%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
										title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
					<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
										title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
					<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th style="width: 15%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
										title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Countries</span>
					<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=programme${rkey_param};
										title python:test(skey=='programme', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Programme</span>
					<img tal:attributes="src python:test(skey=='programme', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th><span i18n:translate="" title="not sortable">Link</span></th>
				<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
			</tr>
			<tr tal:repeat="objects objects_list">
				<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
					<td class="checkbox" tal:condition="del_permission" width="4%" valign="top">
						<input tal:condition="python:object in archive" type="checkbox" name="id" tal:attributes="value object/id" />
						<span tal:condition="python:not object in archive">-</span>
					</td>
					<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
					<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
					<a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
						<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
							[<span tal:replace="object/count_comments" />
							<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
						</tal:block>
					</td>
					<td tal:content="python:test(object.coverage, object.coverage, '-')" />
					<td tal:content="python:test(object.programme, object.programme, '-')" />
					<td><a tal:condition="python:object.resourceurl not in ['', 'http://']" tal:attributes="href python:test(object.resourceurl, object.resourceurl, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.resourceurl in ['', 'http://']">-</span></td>
					<td class="edit" tal:condition="edit_permission">
						<a tal:condition="python:not object.hasVersion() and object in archive" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
						<span tal:condition="python:not(not object.hasVersion() and object in archive)">-</span>
					</td>
				</tal:block>
			</tr>
		</table>
		</form>

		<p>
			Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
			Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
			<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
				<span	tal:repeat="page paging_pages">
					<a	class="paging-link-off"
						tal:condition="python:paging_current_page==page"
						tal:content="python:page+1" />
					<a	tal:condition="python:paging_current_page!=page"
						tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
						tal:content="python:page+1" />
				</span>
				<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
					<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
				</span>
		</p>
	</div>
	</tal:block>
	<p>
		<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

		<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
		<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
		</tal:block>
	</p>

	<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
		[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
	</p>
<span tal:replace="structure here/standard_html_footer"/>
"""

        semide_initiatives_smap_projects = """<span tal:replace="structure here/standard_html_header" />

	<tal:block	define="sq python:request.get('sq', '');
						so python:request.get('so', '');
						gz python:request.get('gz', '');
						th python:request.get('th', '');
						pr python:request.get('pr', '');
						sel_lang python:here.gl_get_selected_language();
						sl python:here.utConvertToList(request.get('sl', [sel_lang]));
						ps_start python:request.get('start', 0);
						archive python:here.getObjects();
						skey python:request.get('skey', 'start_date');
						rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
						rkey_param python:test(rkey, '', '&amp;rkey=1');

						langs_querystring python:'&sl:list='.join(sl);
						page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&so=${so}&sl:list=${langs_querystring}&gz=${gz}&th=${th}&pr=${pr};
						results python:here.getProjectsListing(sq, so, sl, skey, rkey, archive, ps_start, gz, th, pr);

						list_paging python:results[0];
						paging_start python:list_paging[0]+1;
						paging_upper python:list_paging[1];
						paging_total python:list_paging[2];
						paging_prev python:list_paging[3];
						paging_next python:list_paging[4];
						paging_current_page python:list_paging[5];
						paging_records_page python:list_paging[6];
						paging_pages python:list_paging[7];

						list_result python:results[1];
						objects_list python:list_result[2];
						objects_delete_all python:list_result[1];
						objects_select_all python:list_result[0]">

	<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
	<!--
		function fCheckSelection()
		{	var frm = document.objectItems;
		var i;
		check = false;
		for(i=0; i<frm.elements.length; i++)
			if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
			{	check = true; break;}
			return check;}
	//-->
	</script>

	<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
	<!--
		function fDeleteObjects()
		{	if (fCheckSelection())
		{	document.objectItems.action="deleteObjects";
		document.objectItems.submit();}
		else
		alert('Please select one or more items to delete.');}
	//-->
	</script>

	<div id="right_port">
		<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
			<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
		</tal:block>
	</div>

	<div class="middle_port">
		<h1>
			<tal:block tal:replace="here/title_or_id" />
			<tal:block tal:condition="here/can_be_seen">
				<tal:block tal:condition="here/has_restrictions" i18n:translate="">
					[Limited access]
				</tal:block>
			</tal:block>
			<tal:block tal:condition="python:not here.can_be_seen()" i18n:translate="">
				[Restricted access]
			</tal:block>
		</h1>

		<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

		<tal:block	tal:define="this_absolute_url python:here.absolute_url(0);
								submissions here/process_submissions;
								perm_add_something python:len(submissions)>0;
								perm_edit_object here/checkPermissionEditObject;
								perm_publish_objects here/checkPermissionPublishObjects">
			<div id="admin_this_folder" tal:condition="python:perm_edit_object and perm_publish_objects">
				<span id="submission" tal:condition="perm_add_something">
					<span i18n:translate="" tal:omit-tag="">Submit</span>:
					<select name="typetoadd"
						tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
						<option value="#" i18n:translate="">Type to add</option>
						<option tal:repeat="item submissions"
							tal:attributes="value python:item[0]"
							tal:content="python:item[1]" i18n:translate="" />
					</select>
				</span>
				<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
					<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
					<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span i18n:translate="">Approvals</span></a>
				</tal:block>
			</div>
		</tal:block>

		<fieldset class="search_field"><legend i18n:translate="">Search projects</legend>
			<div class="fieldset_div">
				<form method="get" action="">
					<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
					<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
					<div class="field">
						<label for="sq" i18n:translate="">Query</label>
						<input type="text" name="sq" id="sq" size="30" tal:attributes="value sq" />
					</div>
					<div class="field">
						<label for="pr" i18n:translate="">Programme</label>
						<input type="text" name="pr" id="pr" size="30" tal:attributes="value pr" />
					</div>
					<div class="field">
						<label for="so" i18n:translate="">Organisation</label>
						<input type="text" name="so" id="so" size="30" tal:attributes="value so" />
						<input type="submit" value="Search" i18n:attributes="value" />
					</div>
					<div class="field">
						<label for="th" i18n:translate="">Theme</label>
						<select name="th" id="th">
							<option value="" />
							<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(here.gl_get_selected_language())">
								<option	tal:condition="item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										tal:content="item/theme_name" />
								<option	tal:condition="not:item/theme_name"
										tal:attributes="value item/theme_id;
														selected python:item.theme_id == th"
										i18n:translate="">no translation available</option>
							</tal:block>
						</select>
					</div>
					<div class="field">
						<label for="gz" i18n:translate="">Country</label>
						<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
							<option value="" />
							<tal:block repeat="item langs_list">
								<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
													translation python:item.get_translation_by_language(lang_name)">
									<option	tal:condition="translation"
											tal:attributes="value item/id; selected python:item.id == gz"
											tal:content="translation" />
									<tal:block	condition="not:translation"
												define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
														def_trans python:item.get_translation_by_language(lang_name)">
										<option	tal:condition="def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												tal:content="def_trans" />
										<option	tal:condition="not:def_trans"
												tal:attributes="value item/id; selected python:item.id == gz"
												i18n:translate="">no translation available</option>
									</tal:block>
								</tal:block>
							</tal:block>
						</select>
					</div>
					<div class="clear_float"></div>
					<div class="field-inline" tal:define="selected_language here/gl_get_selected_language">
						<strong i18n:translate="">Languages: </strong>
						<tal:block repeat="item here/gl_get_languages_mapping">
						<input name="sl" type="checkbox"
							tal:attributes="value python:item['code']; checked python:item['code'] in sl; id python:'sl_'+item['code']"
							/><label class="search_language" tal:attributes="for python:'sl_'+item['code']" tal:content="python:item['name']" />
						</tal:block>
					</div>
				</form>
			</div>
		</fieldset>

		<br />

		<h2>
			<span tal:condition="python:sq=='' and so=='' and th=='' and gz=='' and pr==''" i18n:translate="">Projects</span>
			<span tal:condition="python:not(sq=='' and so=='' and th=='' and gz=='' and pr=='')" i18n:translate="">Search results</span>
		</h2>

		<div tal:condition="python:objects_select_all or objects_delete_all">
			<div id="toolbar">
				<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
			</div>
		</div>

		<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No projects available</p>
		<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
		<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
				tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
							sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
							sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
							req_params python:here.getRequestParams(request)">
			<tr>
				<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
				<th style="width: 10%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
										title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
					<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
										title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
					<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th style="width: 15%;">
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
										title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Countries</span>
					<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th>
					<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=programme${rkey_param};
										title python:test(skey=='programme', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Programme</span>
					<img tal:attributes="src python:test(skey=='programme', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
						 width="12" height="12" alt=""/>
					</a>
				</th>
				<th><span i18n:translate="" title="not sortable">Link</span></th>
				<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
			</tr>
			<tr tal:repeat="objects objects_list">
				<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
					<td class="checkbox" tal:condition="del_permission" width="4%" valign="top">
						<input tal:condition="python:object in archive" type="checkbox" name="id" tal:attributes="value object/id" />
						<span tal:condition="python:not object in archive">-</span>
					</td>
					<td class="releasedate" tal:content="python:object.utShowDateTime(object.start_date)" />
					<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
					<a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
						<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
							[<span tal:replace="object/count_comments" />
							<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
						</tal:block>
					</td>
					<td tal:content="python:test(object.coverage, object.coverage, '-')" />
					<td tal:content="python:test(object.programme, object.programme, '-')" />
					<td><a tal:condition="python:object.resourceurl not in ['', 'http://']" tal:attributes="href python:test(object.resourceurl, object.resourceurl, 'http://')" i18n:translate="">[link]</a><span tal:condition="python:object.resourceurl in ['', 'http://']">-</span></td>
					<td class="edit" tal:condition="edit_permission">
						<a tal:condition="python:not object.hasVersion() and object in archive" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
						<span tal:condition="python:not(not object.hasVersion() and object in archive)">-</span>
					</td>
				</tal:block>
			</tr>
		</table>
		</form>

		<p>
			Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
			Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
			<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
				<span	tal:repeat="page paging_pages">
					<a	class="paging-link-off"
						tal:condition="python:paging_current_page==page"
						tal:content="python:page+1" />
					<a	tal:condition="python:paging_current_page!=page"
						tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
						tal:content="python:page+1" />
				</span>
				<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
					<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
						tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
				</span>
		</p>
	</div>
	</tal:block>
	<p>
		<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

		<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
		<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
		</tal:block>
	</p>

	<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
		[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
	</p>
<span tal:replace="structure here/standard_html_footer"/>
"""

        semide_thematicdirs_news = """<span tal:replace="structure here/standard_html_header" />
<div class="middle_port" style='margin-right:0;'>
<tal:block	define="sq python:request.get('sq', '');
					sl python:here.utConvertToList(request.get('sl', []));
					nt python:request.get('nt', '');
					nd python:request.get('nd', '');
					nc python:request.get('nc', '');
					ps_start python:request.get('start', 0);
					skey python:request.get('skey', 'news_date');
					rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
					rkey_param python:test(rkey, '', '&amp;rkey=1');

					page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&nt=${nt}&nc=${nc}&nd=${nd};
					results python:here.getNewsListing(sq, sl, nt, nd, nc, skey, rkey, here.absolute_url(1), ps_start);

					list_paging python:results[0];
					paging_start python:list_paging[0]+1;
					paging_upper python:list_paging[1];
					paging_total python:list_paging[2];
					paging_prev python:list_paging[3];
					paging_next python:list_paging[4];
					paging_current_page python:list_paging[5];
					paging_records_page python:list_paging[6];
					paging_pages python:list_paging[7];

					list_result python:results[1];
					objects_list python:list_result[2];
					objects_delete_all python:list_result[1];
					objects_select_all python:list_result[0]">

<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
<!--
	function fCheckSelection()
	{	var frm = document.objectItems;
	var i;
	check = false;
	for(i=0; i<frm.elements.length; i++)
		if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
		{	check = true; break;}
		return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
<!--
	function fDeleteObjects()
	{	if (fCheckSelection())
	{	document.objectItems.action="deleteObjects";
	document.objectItems.submit();}
	else
	alert('Please select one or more items to delete.');}
//-->
</script>

<div id="right_port">
	<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<h1><img tal:attributes="src python:test(here.approved, here.icon, here.icon_marked); title here/meta_label; alt here/meta_label" border="0" /> <tal:block tal:replace="here/title_or_id" /></h1>
<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<tal:block tal:define="submissions here/process_submissions;
		perm_add_something python:len(submissions)>0;
		perm_edit_object here/checkPermissionEditObject;
		perm_publish_objects here/checkPermissionPublishObjects">
<div id="admin_this_folder" tal:condition="python:perm_add_something or perm_edit_object and perm_publish_objects">
	<span id="submission" tal:condition="perm_add_something">
		<span i18n:translate="" tal:omit-tag="">Submit</span>:
		<select name="typetoadd"
				tal:attributes="onchange string:document.location.href='${here/absolute_url}/' + this.options[this.selectedIndex].value">
			<option value="#" i18n:translate="">Type to add</option>
			<option tal:repeat="item submissions"
					tal:attributes="value python:item[0]"
					tal:content="python:item[1]" i18n:translate="" />
		</select>
	</span>
	<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
		<a tal:condition="perm_edit_object" tal:attributes="href string:${here/absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit folder</span></span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${here/absolute_url}/basketofapprovals_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Approvals</span></span></a>
	</tal:block>
</div>
</tal:block>

<fieldset class="search_field"><legend i18n:translate="">Search news</legend>
<div class="fieldset_div">
<form method="get" action="">
<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
<div class="field">
	<label for="sq" i18n:translate="">Query</label>
	<input type="text" name="sq" id="sq" size="50" tal:attributes="value sq" />
</div>
<div class="field">
	<label for="nt" i18n:translate="">Type</label>
	<select name="nt" id="nt">
		<option value=""></option>
		<option tal:repeat="item here/getNewsTypesList"
				tal:attributes="value item/id; selected python:item.id == nt"
				tal:content="item/title" i18n:translate="" />
	</select>
</div>
<div class="field">
	<label for="nd" i18n:translate="">News date</label>
	<select name="nc" id="nc">
		<option value="0" tal:attributes="selected python:nc=='0'">before</option>
		<option value="1" tal:attributes="selected python:nc=='1'">after</option>
	</select
	><input type="text" name="nd" id="nd" size="10" tal:attributes="value nd" />
	<em>(dd/mm/yyyy)</em>
	<input type="submit" value="Search" i18n:attributes="value" />
</div>
<div class="clear_float"></div>
</form>
</div>
</fieldset>

<h2><span tal:condition="python:sq=='' and sl==[] and nt=='' and nd==''" i18n:translate="">News</span><span tal:condition="python:not(sq=='' and sl==[] and nt=='' and nd=='')" i18n:translate="">Search results</span></h2>

<div tal:condition="python:objects_select_all or objects_delete_all">
	<div id="toolbar">
		<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
	</div>
</div>

<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No news available</p>
<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
		tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
					sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
					sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
					req_params python:here.getRequestParams(request)">
	<tr>
		<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=news_date${rkey_param};
								title python:test(skey=='news_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">News date</span>
			<img tal:attributes="src python:test(skey=='news_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
								title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
			<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th style="width: 15%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
								title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Location</span>
			<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=contributor${rkey_param};
								title python:test(skey=='contributor', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Author</span>
			<img tal:attributes="src python:test(skey=='contributor', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
	</tr>
	<tr tal:repeat="objects objects_list">
		<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
			<td class="checkbox" tal:condition="del_permission" width="4%" valign="top"><input type="checkbox" name="id" tal:attributes="value object/id" /></td>
			<td class="releasedate"><span tal:replace="python:object.utShowDateTime(object.news_date)" /></td>
			<td class="title-column">
				<img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
				<a tal:attributes="href object/absolute_url;title python:here.stripAllHtmlTags(object.description)" tal:content="object/title_or_id" />
				<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
					[<span tal:replace="object/count_comments" />
					<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
				</tal:block>
			</td>
			<td tal:content="python:test(object.coverage, object.coverage, '-')" />
			<td tal:content="object/contributor" />
			<td class="edit" tal:condition="edit_permission">
				<a tal:condition="python:not object.hasVersion()" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
			</td>
		</tal:block>
	</tr>
</table>
</form>

<p>
	Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
	Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
	<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
		tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
		<span	tal:repeat="page paging_pages">
			<a	class="paging-link-off"
				tal:condition="python:paging_current_page==page"
				tal:content="python:page+1" />
			<a	tal:condition="python:paging_current_page!=page"
				tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
				tal:content="python:page+1" />
		</span>
		<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
			<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
		</span>
</p>

</tal:block>

<p>
	<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

	<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
	<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
	</tal:block>
</p>

<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
	[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
</p>
</div>
<span tal:replace="structure here/standard_html_footer"/>
"""

        semide_documents_database_search_html = """<span tal:replace="structure here/standard_html_header" />
<tal:block	define="sel_lang python:here.gl_get_selected_language();
					sq python:request.get('sq', '');
					sl python:here.utConvertToList(request.get('sl', []));
					mt python:here.utConvertToList(request.get('mt', []));
					tp python:here.utConvertToList(request.get('tp', []));
					dp python:here.utConvertToList(request.get('dp', []));
					mp python:here.utConvertToList(request.get('mp', []));
					sd python:request.get('sd', '');
					ed python:request.get('ed', '');
					lh python:request.get('lh', '');
					th python:request.get('th', '');

					ps_start python:request.get('start', 0);
					skey python:request.get('skey', 'date');
					rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
					rkey_param python:test(rkey, '', '&amp;rkey=1');

					sl_querystring python:'&sl:list='.join(sl);
					mt_querystring python:'&mt:list='.join(mt);
					tp_querystring python:'&tp:list='.join(tp);
					dp_querystring python:'&dp:list='.join(dp);
					mp_querystring python:'&mp:list='.join(mp);
					page_search_querystring string:sq=${sq}&th=${th}&sd=${sd}&ed=${ed}&lh=${lh}&skey=${skey}&rkey=${rkey}&sl:list=${sl_querystring}&mt:list=${mt_querystring}&tp:list=${tp_querystring}&dp:list=${dp_querystring}&mp:list=${mp_querystring};

					results python:here.getResourceListing(sq, mt, tp, dp, mp, sd, ed, sl, th, skey, rkey, ps_start);

					list_paging python:results[0];
					paging_start python:list_paging[0]+1;
					paging_upper python:list_paging[1];
					paging_total python:list_paging[2];
					paging_prev python:list_paging[3];
					paging_next python:list_paging[4];
					paging_current_page python:list_paging[5];
					paging_records_page python:list_paging[6];
					paging_pages python:list_paging[7];

					list_result python:results[1];
					objects_list python:list_result[2];
					objects_delete_all python:list_result[1];
					objects_select_all python:list_result[0]">

<div id="right_port">
	<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<script language="javascript" type="text/javascript">
<!--
function fPick(glossary_url)
{
	var wnd = window.open(glossary_url, "pickkeywordforsearch", "height=400,width=500,status=no,resizable=no,toolbar=no,menubar=no,location=no,scrollbars=yes");
	wnd.focus();
}

function fSet(ctrl, value)
{
	var frm = document.frmSearch;
	var items = frm[ctrl];
	if (value != '')
	{
		if (items.value == '')
			items.value = value;
		else
			items.value = items.value + ' or ' + value;
	}
}
// -->
</script>

<h1><img tal:attributes="src python:test(here.approved, here.icon, here.icon_marked); title here/meta_label; alt here/meta_label" border="0" /> <tal:block tal:replace="here/title_or_id" /> - <span i18n:translate="">search resources</span></h1>
<p i18n:translate="">This form allows you to search texts of laws, documents and multimedia articles inside this folder.</p>

<form method="get" action="" name="frmSearch">
<div class="field-inline">
	<label for="sq" i18n:translate="" style="position:relative;">Query</label>
	<span style="white-space:nowrap;">
		<input style="vertical-align:middle;" type="text" name="sq" id="sq" size="50" tal:attributes="value sq" />
		<label for="pick-keywords" class="invisible">Pick term</label><input type="button" value="Pick term" id="pick-keywords" tal:attributes="onclick string:javascript:fPick('portal_thesaurus/GlossMap_html?ctrl=sq&amp;lang=${sel_lang}');" />
	</span>
</div><br />

<script type="text/javascript" language="javascript">

function MM_findObj(n, d) { //v4.01
	var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
		d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
	if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
	for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
	if(!x && d.getElementById) x=d.getElementById(n); return x;
}

	function metatypeSelection(p_this, p_targets){
		l_targets = p_targets.split(" ")
		for(i in l_targets){
			ob = MM_findObj(l_targets[i])
			if (p_this.checked) {
				ob.style.display = 'block'
			} else {
				ob.style.display = 'none'
			}
		}
	}

	var SELECT_ALL
	var DESELECT_ALL
	var z_texts_of_laws = new Array()
	var z_documents = new Array()
	var z_multimedia = new Array()
	function typesSelectDeselect(p_this, p_target_array, p_label){
		ob = MM_findObj(p_label)
		if(p_this.checked) {
			ob.innerHTML = DESELECT_ALL
		} else {
			ob.innerHTML = SELECT_ALL
		}
		for(i in p_target_array){
			ob = MM_findObj(p_target_array[i])
			ob.checked = p_this.checked
		}
	}

	function setDeselectText(p_targets){
		ob = MM_findObj('text_select_all')
		SELECT_ALL = ob.innerHTML
		ob = MM_findObj('text_deselect_all')
		DESELECT_ALL = ob.innerHTML
		l_targets = p_targets.split(" ")
		for(i in l_targets){
			ob = MM_findObj(l_targets[i])
			ob.innerHTML = DESELECT_ALL
		}
	}

	function checkSelections(){
		metatypeSelection(MM_findObj('options_advanced'), 'field_advanced')
		metatypeSelection(MM_findObj('NySemTextLaws'), 'field_texts_of_laws')
		metatypeSelection(MM_findObj('NySemDocument'), 'field_documents')
		metatypeSelection(MM_findObj('NySemMultimedia'), 'field_multimedia')
	}

</script>

<div style="padding:5px 5px; background-color: #f8f8f8">

<div id="field_advanced_check" style="margin-bottom:10px; display:none;">
	<input onclick="metatypeSelection(this, 'field_advanced')" type="checkbox" name="lh" value="" id="options_advanced" tal:condition="python:request.QUERY_STRING==''" checked="checked" style="position:relative;top:-3px;" />
	<input onclick="metatypeSelection(this, 'field_advanced')" type="checkbox" name="lh" value=""  id="options_advanced" tal:condition="python:request.QUERY_STRING" style="position:relative;top:-3px;" />
	<label for="options_advanced" style="position:relative;" i18n:translate>Display more search options</label>
</div>

<div id="field_advanced">
	<div class="columns_more">
		<fieldset style="width:150px;">
			<legend i18n:translate="">Languages</legend>
			<div class="fieldset_div">
				<ul class="checklist" tal:define="selected_language sel_lang">
					<li tal:repeat="item here/gl_get_languages_mapping">
						<input type="checkbox" name="sl"
							tal:attributes="value python:item['code']; id python:item['code']"
							tal:condition="python:item['code']==selected_language"
							checked="checked" />
						<input type="checkbox" name="sl"
							tal:attributes="value python:item['code']; id python:item['code']"
							tal:condition="python:item['code']!=selected_language" /><label tal:attributes="for python:item['code']" tal:content="python:item['name']" i18n:translate="" />
					</li>
				</ul>
			</div>
		</fieldset>
	</div>

	<div class="columns_more">
		<fieldset style="width:300px;">
			<legend i18n:translate="">Published between</legend>
			<div class="fieldset_div">
				<p i18n:translate="">Insert date(s) in <strong>dd/mm/yyyy</strong> format</p>
				<div class="checklist">
					<input type="text" name="sd" size="10" tal:attributes="value sd" /> and <input type="text" name="ed" size="10" tal:attributes="value ed" />
				</div>
			</div>
		</fieldset>
	</div>

	<div class="clear_float">&nbsp;</div>

	<fieldset class="columns_more">
		<legend i18n:translate="">Themes</legend>
		<div class="fieldset_div">
			<div class="checklist">
				<select name="th" id="th">
					<option value="" />
					<tal:block repeat="item python:here.getPortalThesaurus().getThemesList(sel_lang)">
						<option	tal:condition="item/theme_name"
								tal:attributes="value item/theme_id;
												selected python:item.theme_id == th"
								tal:content="item/theme_name" />
						<option	tal:condition="not:item/theme_name"
								tal:attributes="value item/theme_id;
												selected python:item.theme_id == th"
								i18n:translate="">no translation available</option>
					</tal:block>
				</select>
			</div>
		</div>
	</fieldset>

	<div class="clear_float">&nbsp;</div>

	<h2 style="position:relative;">Document types to search</h2>

	<fieldset class="columns_more">
		<legend i18n:translate="">Text of laws</legend>
		<div class="fieldset_div">
			<input onclick="metatypeSelection(this, 'field_texts_of_laws')" type="checkbox"
				id="NySemTextLaws" name="mt" value="Naaya Semide Text of Laws"
				checked="checked" tal:condition="python:('Naaya Semide Text of Laws' in mt) or (request.QUERY_STRING=='')" />
			<input onclick="metatypeSelection(this, 'field_texts_of_laws')" type="checkbox"
				 id="NySemTextLaws" name="mt" value="Naaya Semide Text of Laws"
				tal:condition="python:('Naaya Semide Text of Laws' not in mt) and (request.QUERY_STRING)" /><label for="NySemTextLaws" i18n:translate="">Search texts of laws</label>

			<div id="field_texts_of_laws">
				<select id="frm_tp" name="tp:list" multiple="multiple" size="5">
				<tal:block repeat="item here/getTextLawsTypesList">
					<option tal:attributes="value item/id; selected python:item.id in tp"
							tal:content="item/title" />
				</tal:block>
				</select>
			</div>
		</div>
	</fieldset>

	<fieldset class="columns_more">
		<legend i18n:translate="">Documents</legend>
		<div class="fieldset_div">
			<input onclick="metatypeSelection(this, 'field_documents')" type="checkbox" id="NySemDocument" name="mt"
			checked="checked" value="Naaya Semide Document" tal:condition="python:('Naaya Semide Document' in mt) or (request.QUERY_STRING=='')" />
			<input onclick="metatypeSelection(this, 'field_documents')" type="checkbox" id="NySemDocument" name="mt"
			value="Naaya Semide Document" tal:condition="python:('Naaya Semide Document' not in mt) and (request.QUERY_STRING)" /><label for="NySemDocument" i18n:translate="">Search documents</label>

			<div id="field_documents">
				<select id="frm_dp" name="dp:list" multiple="multiple" size="5">
				<tal:block repeat="item here/getDocumentTypesList">
					<option tal:attributes="value item/id; selected python:item.id in tp"
							tal:content="item/title" />
				</tal:block>
				</select>
			</div>
		</div>
	</fieldset>

	<fieldset class="columns_more">
		<legend i18n:translate="">Multimedia</legend>
		<div class="fieldset_div">
			<input onclick="metatypeSelection(this, 'field_multimedia')" type="checkbox" id="NySemMultimedia" name="mt"
			checked="checked" value="Naaya Semide Multimedia"
			tal:condition="python:('Naaya Semide Multimedia' in mt) or (request.QUERY_STRING=='')" />
			<input onclick="metatypeSelection(this, 'field_multimedia')" type="checkbox" id="NySemMultimedia" name="mt"
			value="Naaya Semide Multimedia"
			tal:condition="python:('Naaya Semide Multimedia' not in mt) and (request.QUERY_STRING)" /><label for="NySemMultimedia" i18n:translate="">Search multimedia</label>

			<div id="field_multimedia">
				<select id="frm_mp" name="mp:list" multiple="multiple" size="4">
				<tal:block repeat="item here/getMultimediaTypesList">
					<option tal:attributes="value item/id; selected python:item.id in tp"
							tal:content="item/title" />
				</tal:block>
				</select>
			</div>
		</div>
	</fieldset>
	<div class="clear_float">&nbsp;</div>
</div>
</div>
	<div class="field">
		<input type="submit" value="Search" i18n:attributes="value" />
	</div>
</form>

<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No documents available</p>
<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
		tal:condition="python:len(objects_list) > 0"
		tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
					sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
					sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
					req_params python:here.getRequestParams(request)">
<thead>
	<tr>
		<th style="width: 10%;">
			<a	tal:attributes="href string:${here/absolute_url}/search_html?${req_params}skey=date${rkey_param};
								title python:test(skey=='date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Release date</span>
			<img tal:attributes="src python:test(skey=='date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>

		<th style="width: 40%;">
			<a	tal:attributes="href string:${here/absolute_url}/search_html?${req_params}skey=title${rkey_param};
								title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
			<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>

		<th style="width: 20%;"><span i18n:translate="" title="not sortable">Doc. type</span></th>
		<!--
		<th style="width: 20%;">
			<a	tal:attributes="href string:${here/absolute_url}/search_html?${req_params}skey=type${rkey_param};
								title python:test(skey=='type', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Doc. type</span>
			<img tal:attributes="src python:test(skey=='type', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		-->

		<th style="width: 20%;">
			<a	tal:attributes="href string:${here/absolute_url}/search_html?${req_params}skey=source${rkey_param};
								title python:test(skey=='source', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Source</span>
			<img tal:attributes="src python:test(skey=='source', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>

		<th style="width: 10%;"><span i18n:translate="" title="not sortable">Link</span></th>
	</tr>
</thead>
<tbody>
	<tr tal:repeat="objects objects_list">
		<tal:block define="edit_permission python:objects[1]; object python:objects[2]">
			<td class="releasedate"><span tal:replace="python:object.utShowDateTime(object.releasedate)"/></td>
			<td class="title-column">
				<img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" /> <a tal:attributes="href object/absolute_url;title object/description" tal:content="object/title_or_id" />
				<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
					[<span tal:replace="object/count_comments" />
					<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
				</tal:block>
			</td>
			<td tal:content="python:object.resource_type()" />
			<td tal:define="ob_src object/source">
				<span tal:condition="ob_src" tal:content="ob_src" />
				<span tal:condition="not:ob_src" i18n:translate="">N/A</span>
			</td>
			<td>
				[<a tal:attributes="href object/file_link">File link</a>]
			</td>
		</tal:block>
	</tr>
</tbody>
</table>

<p>
	Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
	Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
	<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
		tal:attributes="href string:${url}/search_html?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
		<span	tal:repeat="page paging_pages">
			<a	class="paging-link-off"
				tal:condition="python:paging_current_page==page"
				tal:content="python:page+1" />
			<a	tal:condition="python:paging_current_page!=page"
				tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
				tal:attributes="href string:${url}/search_html?start=${start_batch}&${page_search_querystring}"
				tal:content="python:page+1" />
		</span>
		<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
			<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
				tal:attributes="href string:${url}/search_html?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
		</span>
</p>

<p>
	<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

	<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
	<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${sel_lang}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
	</tal:block>
</p>

<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
	[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
</p>

</tal:block>
<span tal:replace="structure here/standard_html_footer"/>
"""

        site_admin_centre = """<tal:block metal:use-macro="python:here.getFormsTool().site_admin_template.macros['page']">

<h1 metal:fill-slot="title" i18n:translate="">Portal administration centre</h1>

<tal:block metal:fill-slot="section">
	<p i18n:translate="">This section allows administrators to manage the content, the look &amp; feel and maintain various functions of the current portal.</p>

	<p><strong i18n:translate="">All administration functionalities are available from the right-side menu.</strong></p>

	<p><img src="misc_/Naaya/admin_schema" border="0" alt="Overview of the administrative functionality" i18n:attributes="alt" /></p>
</tal:block>

</tal:block>"""

        site_admin_messages = """<tal:block metal:use-macro="python:here.getFormsTool().site_admin_template.macros['page']">

<h1 metal:fill-slot="title" i18n:translate="">Translate message</h1>

<tal:block metal:fill-slot="section"
	tal:define="site_url here/getSitePath;
			query python:request.get('query', '');
			start python:request.get('start', '');
			skey python:request.get('skey', 'msg');
			rkey python:request.get('rkey', '');
			sort_qs python:'start=%s&amp;skey=%s&amp;rkey=%s&amp;query=%s' % (start, skey, rkey, query);
			catalog here/getPortalTranslations;
			languages python:catalog.tt_get_languages_mapping();
			msg_encoded python:request.get('msg', '');
			message python:catalog.message_decode(msg_encoded)">

<p>
	<a tal:attributes="href string:${site_url}/admin_translations_html?${sort_qs}"
		i18n:translate="">Back to translation form</a>
</p>

<fieldset>
	<legend i18n:translate="">Original label in English language.</legend>
	<div style="padding:1em;background-color:#f0f0f0;" tal:content="message" />
</fieldset>

<p i18n:translate="">
	You can translate this message in the following languages.
</p>

<tal:block tal:repeat="language languages">
<fieldset>
	<legend  tal:content="python:language['name']" />
	<form method="post" tal:attributes="action string:${site_url}/admin_editmessage">
		<div><textarea name="translation:utf8:ustring" cols="60" rows="6" wrap="off" tal:content="python:catalog.get_msg_translations(message, language['code'])" /></div>
		<input type="hidden" name="message:utf8:ustring" tal:attributes="value message" />
		<input type="hidden" name="language" tal:attributes="value python:language['code']">
		<input type="hidden" name="start" tal:attributes="value start" />
		<input type="hidden" name="skey" tal:attributes="value skey" />
		<input type="hidden" name="rkey" tal:attributes="value rkey" />
		<input type="hidden" name="query" tal:attributes="value query" />
		<input type="submit" value="Save changes" i18n:attributes="value" />
		<input type="reset" value="Reset" i18n:attributes="value" />
	</form>
</fieldset>
</tal:block>

</tal:block>

</tal:block>"""

        semide_site_header = """<span tal:replace="python:request.RESPONSE.setHeader('content-type','text/html;charset=utf-8')" />
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	tal:attributes="xml:lang here/gl_get_selected_language; lang here/gl_get_selected_language; dir python:test(isArabic, 'rtl', 'ltr')"
	tal:define="site_url here/getSitePath; isArabic here/isArabicLanguage; noArabic not:isArabic">
	<head>
		<title tal:content="here/title_or_id" />
		<link rel="icon" href="../favicon.ico" />
		<link rel="stylesheet" type="text/css" media="screen" tal:attributes="href string:${skin_files_path}/style" />
		<link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${skin_files_path}/style_common" />
		<link rel="stylesheet" type="text/css" media="print" tal:attributes="href string:${skin_files_path}/style_print" />
		<link rel="stylesheet" type="text/css" media="handheld" tal:attributes="href string:${skin_files_path}/style_handheld" />
		<link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${site_url}/glossary_coverage/style_presentation_css" />
		<link rel="stylesheet" type="text/css" media="all" tal:attributes="href string:${site_url}/portal_thesaurus/thesaurus_css" />
		<link rel="home" tal:attributes="href python:request['BASE0']" title="Home" />
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
		<meta name="description" tal:attributes="content here/title_or_id" />
		<!--[if IE]>
			<style type="text/css">
			/*<![CDATA[*/ 
			body {
				word-wrap: break-word;
			}
			/*]]>*/
			</style>
		<![endif]-->
	</head>
	<body>
		<a class="skiplink" href="#contentstart" accesskey="2" i18n:translate="">Skip navigation</a>
		<div class="white_backgrounded">
			<div id="nav_upper" tal:define="authenticated_user python:request.AUTHENTICATED_USER.getUserName()">
				<div tal:define="l_list python:here.getPortletsTool().getLinksListById('menunav_links').get_links_list()">

					<div id="nav_upper_log">
						
						<img tal:attributes="src string:${here/getSkinFilesPath}/ico_login.gif;" align="middle" alt="" />
						<tal:block tal:condition="python: authenticated_user != 'Anonymous User'">
							<span i18n:translate="" tal:omit-tag="">you are logged in as</span>
							<strong tal:content="authenticated_user" />
							<a tal:attributes="href string:${site_url}/login_html" i18n:translate="">logout</a>
						</tal:block>

						<tal:block tal:condition="python: authenticated_user == 'Anonymous User'">
							<span i18n:translate="" tal:omit-tag="">you are not logged in</span>
							<a tal:attributes="href string:${site_url}/login_html" i18n:translate="">login</a>
							<a tal:attributes="href string:${site_url}/requestrole_html" i18n:translate="">create account</a>
						</tal:block>
						
					</div>


					<span><a tal:attributes="href site_url" i18n:translate="" accesskey="1">Home</a> </span>
					<span tal:condition="python:authenticated_user=='Anonymous User'"><a tal:attributes="href string:${here/getFlashToolPath}/subscribe_html" i18n:translate="">e-Flash</a> </span>
					<span tal:condition="python:authenticated_user!='Anonymous User'"><a tal:attributes="href string:${here/getFlashToolPath}/profilesheet_html" i18n:translate="">e-Flash</a> </span>
					<span tal:condition="python:authenticated_user!='Anonymous User'"><a tal:attributes="href string:${site_url}/profilesheet_html" i18n:translate="">My portal</a> </span>

					<tal:block tal:repeat="item l_list">
					<span tal:condition="python:here.checkPermissionForLink(item.permission, here)"><a tal:attributes="href python:test(item.relative, '%s%s' % (site_url, item.url), item.url); title item/description" tal:content="item/title" i18n:translate="" i18n:attributes="title">Title</a> </span>
					</tal:block>
				</div>

			</div>
			<div class="clearing_div_top"> &nbsp; </div>
<!-- top banner -->
			<div id="top_banner">
				<div id="banner_images" tal:define="thumb_list here/getThumbs;
													thumb1 python:thumb_list[0];
													thumb2 python:thumb_list[1];
													thumb3 python:thumb_list[2]">
					<img tal:attributes="src thumb1" alt="" />
					<img tal:attributes="src thumb2" alt="" />
					<img tal:attributes="src thumb3" alt="" />
				</div>
				<div id="site_logo">
					<img tal:attributes="src string:${here/getLayoutToolPath}/logo.gif" alt="" />
				</div>
				<div id="site_title">
					<span tal:content="here/site_title" />
					<div id="site_subtitle" tal:content="here/site_subtitle" />
				</div>
			</div>
<!--END top banner -->
<!-- top menu -->
			<div id="nav_main">
				<div id="nav_main_language">
					<tal:block replace="structure here/languages_box" />
				</div>
				<div id="nav_main_links">

<!-- LIST CONTAINING THE GLOBAL LEVEL -->

					<ul>
						<li tal:repeat="main_categ here/getMainTopics">
							<a tal:attributes="href string:${main_categ/absolute_url}; title main_categ/tooltip" tal:content="main_categ/title" />
							<span tal:condition="isArabic">&nbsp;|&nbsp;</span>
						</li>
					</ul>


<!-- END OF LIST CONTAINING THE GLOBAL LEVEL -->

				
				</div>
			</div>
<!--END top menu -->
<!-- acces-bread-search -->
			<div id="bar_divided">
				<div id="quick_acces">
					<form method="get" tal:attributes="action string:${site_url}/getQuickAccess">
						<label accesskey="5" for="query1" i18n:translate="">Quick access: </label>
						<select	style="color:#999999;" id="query1" name="qa_url" onclick="this.style.color='#000000'"
								tal:define="l_list python:here.getPortletsTool().getLinksListById('quick_access').get_links_list()">
							<tal:block tal:repeat="item l_list">
							<option	tal:condition="python:here.checkPermissionForLink(item.permission, here)"
									tal:attributes="value python:test(item.relative, '%s%s' % (site_url, item.url), item.url); title item/description"
									tal:content="item/title"
									i18n:translate="" />
							</tal:block>
						</select>
						<input tal:attributes="src string:${here/getSkinFilesPath}/ico_quickaccess.gif" id="sub1" type="image" name="submit" i18n:attributes="alt;title" alt="Quick access" title="Quick access" />
					</form>
				</div>
				<div id="search_area">
					<form method="get" tal:attributes="action string:${site_url}/search_html">
						<label accesskey="4" for="query" i18n:translate="">Site search: </label>
						<input id="query" type="text" name="query" i18n:attributes="value" value="Search" style="color:#999999" onclick="this.value='';this.style.color='#000000'" />
						<input tal:attributes="src string:${here/getSkinFilesPath}/ico_sitesearch.gif" id="sub" type="image" name="submit" i18n:attributes="alt;title" alt="Search" title="Search" />
					</form>
				</div>
				<div id="bread_crumb_trail">
						<tal:block repeat="crumb python:here.getBreadCrumbTrail(request)">
						<a tal:condition="python:crumb.meta_type!='SEMIDE Site'"
						   tal:attributes="href string:${crumb/absolute_url}/;
										   title crumb/title_or_id;"
						   tal:content="crumb/title_or_id" />
						<a tal:condition="python:crumb.meta_type=='SEMIDE Site'" tal:attributes="href site_url"
						   i18n:translate="">
							Home
						</a>
						<span tal:condition="not:repeat/crumb/end"> &raquo; </span>
						</tal:block>
				</div>
			</div>

		</div>
<!--END acces-bread-search -->
<div class="clearing_div"> &nbsp; </div>

	<div id="main_structure_ie_fixer">
		<div id="main_structure">

<!-- LEFT SIDE PORTLETS -->
			<div id="left_port">
				<br/>

				<tal:block tal:repeat="item here/get_left_portlets_objects">
					<tal:block tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_left_macro'})" />
				</tal:block>


			</div>
<!-- END OF LEFT SIDE PORTLETS -->
<tal:block condition="isArabic" replace="structure string:<table width='100%'><tr><td>" />

			<div id="middle_right_port">
			<span tal:replace="structure here/messages_box"/>
				<a name="contentstart" id="contentstart"></a>
				<!--SITE_HEADERFOOTER_MARKER-->

			</div>
		</div>
	</div>
	</body>
</html>"""

        semide_thematicdirs_events = """<span tal:replace="structure here/standard_html_header" />
<div class="middle_port" style='margin-right:0;'>
<tal:block define="sq python:request.get('sq', '');
	sl python:here.utConvertToList(request.get('sl', []));
	et python:request.get('et', '');
	gz python:request.get('gz', '');
	es python:request.get('es', '');
	sd python:request.get('sd', '');
	ed python:request.get('ed', '');
	ps_start python:request.get('start', 0);
	skey python:request.get('skey', 'start_date');
	rkey python:request.get('rkey', test(request.has_key('skey'),'','1'));
	rkey_param python:test(rkey, '', '&amp;rkey=1');

	page_search_querystring string:sq=${sq}&skey=${skey}&rkey=${rkey}&et=${et}&gz=${gz}&es=${es}&sd=${sd}&ed=${ed};
	results python:here.getEventsListing(sq, sl, et, gz, es, skey, rkey, sd, ed, here.absolute_url(1), ps_start);

	list_paging python:results[0];
	paging_start python:list_paging[0]+1;
	paging_upper python:list_paging[1];
	paging_total python:list_paging[2];
	paging_prev python:list_paging[3];
	paging_next python:list_paging[4];
	paging_current_page python:list_paging[5];
	paging_records_page python:list_paging[6];
	paging_pages python:list_paging[7];

	list_result python:results[1];
	objects_list python:list_result[2];
	objects_delete_all python:list_result[1];
	objects_select_all python:list_result[0]">

<script language="javascript" type="text/javascript" tal:condition="objects_select_all">
<!--
	function fCheckSelection()
	{	var frm = document.objectItems;
	var i;
	check = false;
	for(i=0; i<frm.elements.length; i++)
		if (frm.elements[i].type == "checkbox" && frm.elements[i].name == "id" && frm.elements[i].checked)
		{	check = true; break;}
		return check;}
//-->
</script>

<script language="javascript" type="text/javascript" tal:condition="objects_delete_all">
<!--
	function fDeleteObjects()
	{	if (fCheckSelection())
	{	document.objectItems.action="deleteObjects";
	document.objectItems.submit();}
	else
	alert('Please select one or more items to delete.');}
//-->
</script>

<div class="right_port">
	<tal:block tal:repeat="item python:here.get_right_portlets_locations_objects(here)">
		<span tal:replace="structure python:item({'here': here, 'portlet_macro': 'portlet_right_macro'})" />
	</tal:block>
</div>

<h1><img tal:attributes="src python:test(here.approved, here.icon, here.icon_marked); title here/meta_label; alt here/meta_label" border="0" /> <tal:block tal:replace="here/title_or_id" /></h1>
<p tal:condition="python:here.description!=''" tal:content="structure here/description" />

<tal:block tal:define="this_absolute_url python:here.absolute_url(0);
	submissions here/process_submissions;
	perm_add_something python:len(submissions)>0;
	perm_edit_object here/checkPermissionEditObject;
	perm_publish_objects here/checkPermissionPublishObjects">
<div id="admin_this_folder" tal:condition="python:perm_add_something or perm_edit_object and perm_publish_objects">
	<span id="submission" tal:condition="perm_add_something">
		<span i18n:translate="" tal:omit-tag="">Submit</span>:
		<select name="typetoadd"
				tal:attributes="onchange string:document.location.href='${this_absolute_url}/' + this.options[this.selectedIndex].value">
			<option value="#" i18n:translate="">Type to add</option>
			<option tal:repeat="item submissions"
					tal:attributes="value python:item[0]"
					tal:content="python:item[1]" i18n:translate="" />
		</select>
	</span>
	<tal:block tal:condition="python:perm_edit_object or perm_publish_objects">
		<a tal:condition="perm_edit_object" tal:attributes="href string:${this_absolute_url}/edit_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Edit Folder</span></span></a>
		<a tal:condition="perm_publish_objects" tal:attributes="href string:${this_absolute_url}/basketofapprovals_html"><span class="buttons"><span i18n:translate="" tal:omit-tag="">Approvals</span></span></a>
	</tal:block>
</div>
</tal:block>


<fieldset class="search_field"><legend i18n:translate="">Search events</legend>
	<div class="fieldset_div">
		<form method="get" action="">
		<input type="hidden" name="skey" id="skey" tal:attributes="value skey" />
		<input type="hidden" name="rkey" id="rkey" tal:attributes="value rkey" />
		<div class="field">
			<label for="sq" i18n:translate="">Query</label>
			<input type="text" name="sq" id="sq" size="50" tal:attributes="value sq" />
		</div>
		<div class="field">
			<label for="et" i18n:translate="">Type</label>
			<select name="et" id="et">
				<option value=""></option>
				<option tal:repeat="item here/getEventTypesList"
					tal:attributes="value item/id; selected python:item.id==et" tal:content="item/title" i18n:translate="" />
			</select>
		</div>
		<div class="field">
			<label for="es" i18n:translate="">Status</label>
			<select name="es" id="es">
				<option value=""></option>
				<option tal:repeat="item here/getEventStatusList"
					tal:attributes="value item/id; selected python:item.id==es" tal:content="item/title" i18n:translate="" />
			</select>
		</div>
		<div class="field">
			<label for="gz" i18n:translate="">Location</label>
			<select	name="gz" id="gz" tal:define="langs_list here/getCoverageGlossaryObjects">
				<option value="" />
				<tal:block repeat="item langs_list">
					<tal:block	define="lang_name python:here.gl_get_language_name(here.gl_get_selected_language());
										translation python:item.get_translation_by_language(lang_name)">
						<option	tal:condition="translation"
								tal:attributes="value item/id; selected python:item.id == gz"
								tal:content="translation" />
						<tal:block	condition="not:translation"
									define="lang_name python:here.gl_get_language_name(here.gl_get_default_language());
											def_trans python:item.get_translation_by_language(lang_name)">
							<option	tal:condition="def_trans"
									tal:attributes="value item/id; selected python:item.id == gz"
									tal:content="def_trans" />
							<option	tal:condition="not:def_trans"
									tal:attributes="value item/id; selected python:item.id == gz"
									i18n:translate="">no translation available</option>
						</tal:block>
					</tal:block>
				</tal:block>
			</select>
		</div>
		<div class="clear_float"></div>

		<div class="field" style="margin-top:10px;">
			<span>Start date between:</span>
			<input type="text" name="sd" id="sd" size="10" tal:attributes="value sd" /> and <input type="text" name="ed" id="es" size="10" tal:attributes="value ed" />
			<span>dd/mm/yyyy</span>
			<input type="submit" value="Search" i18n:attributes="value" />
		</div>
		<div class="clear_float"></div>
		</form>
	</div>
</fieldset>

<h2>
	<span tal:condition="python:sq=='' and sl==[] and et=='' and gz=='' and es=='' and ed=='' and sd==''" i18n:translate="">Upcoming events</span>
	<span tal:condition="python:not(sq=='' and sl==[] and et=='' and gz=='' and es=='' and ed=='' and sd=='')" i18n:translate="">Search results</span>
</h2>

<div tal:condition="python:objects_select_all or objects_delete_all">
	<div id="toolbar">
		<tal:block tal:condition="objects_delete_all"><a href="javascript:fDeleteObjects();"><span><span i18n:translate="" tal:omit-tag="">Delete</span></span></a></tal:block>
	</div>
</div>

<p i18n:translate="" tal:condition="python:len(objects_list) == 0">No events available</p>
<form name="objectItems" method="post" action="" tal:condition="python:len(objects_list) > 0">
<table	border="0" cellpadding="0" cellspacing="0" id="folderfile_list" class="sortable"
		tal:define="sortup_gif string:${here/getSitePath}/images/sortup.gif;
					sortnot_gif string:${here/getSitePath}/images/sortnot.gif;
					sortdown_gif string:${here/getSitePath}/images/sortdown.gif;
					req_params python:here.getRequestParams(request)">
	<tr>
		<th class="checkbox" style="width: 5%;" tal:condition="objects_delete_all"><span i18n:translate="" title="not sortable">Delete</span></th>
		<th style="width: 10%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=start_date${rkey_param};
								title python:test(skey=='start_date', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Starting date</span>
			<img tal:attributes="src python:test(skey=='start_date', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=title${rkey_param};
								title python:test(skey=='title', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Title</span>
			<img tal:attributes="src python:test(skey=='title', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th style="width: 15%;">
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=coverage${rkey_param};
								title python:test(skey=='coverage', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Location</span>
			<img tal:attributes="src python:test(skey=='coverage', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th>
			<a	tal:attributes="href string:${here/absolute_url}?${req_params}skey=source${rkey_param};
								title python:test(skey=='source', test(rkey_param, 'sorted ascending', 'sorted descending'), 'sortable')" i18n:attributes="title"><span i18n:translate="" tal:omit-tag="">Source</span>
			<img tal:attributes="src python:test(skey=='source', test(rkey_param, sortup_gif, sortdown_gif), sortnot_gif)"
				 width="12" height="12" alt=""/>
			</a>
		</th>
		<th><span i18n:translate="" title="not sortable">Link</span></th>
		<th class="edit" tal:condition="objects_select_all"><span i18n:translate="" title="not sortable">Edit</span></th>
	</tr>
	<tr tal:repeat="objects objects_list">
		<tal:block define="del_permission python:objects[0]; edit_permission python:objects[1]; object python:objects[2]">
			<td class="checkbox" tal:condition="del_permission" width="4%" valign="top"><input type="checkbox" name="id" tal:attributes="value object/id" /></td>
			<td class="releasedate"><span tal:replace="python:object.utShowDateTime(object.start_date)"/></td>
			<td class="title-column"><img tal:attributes="src python:test(object.approved, object.icon, object.icon_marked); alt python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type); title python:test(hasattr(object, 'meta_label'), object.meta_label, object.meta_type)" border="0" />
			<a tal:attributes="href object/absolute_url;title python:here.stripAllHtmlTags(object.description)" tal:content="object/title_or_id" />
				<tal:block tal:condition="python:object.is_open_for_comments() and object.count_comments()>0">
					[<span tal:replace="object/count_comments" />
					<span tal:omit-tag="" i18n:translate="">comment(s)</span>]
				</tal:block>
			</td>
			<td tal:content="python:test(object.coverage, object.coverage, '-')" />
			<td tal:content="python:test(object.source, object.source, '-')" />
			<td>
				<a tal:condition="python:object.file_link != 'http://'" tal:attributes="href object/file_link" i18n:translate="">[link]</a>
				<span tal:condition="python:object.file_link == 'http://'">-</span>
			</td>
			<td class="edit" tal:condition="edit_permission">
				<a tal:condition="python:not object.hasVersion()" tal:attributes="href string:${object/absolute_url}/edit_html"><img src="misc_/Naaya/edit" border="0" alt="Edit" i18n:attributes="alt" /></a>
			</td>
		</tal:block>
	</tr>
</table>
</form>

<p>
	Results <strong tal:content="paging_start"/>&nbsp;-&nbsp;<strong tal:content="paging_upper"/>&nbsp;of&nbsp;<strong tal:content="paging_total"/><br />
	Page <span tal:condition="python:paging_prev!=-1">&nbsp;&nbsp;
	<a	tal:define="url python:here.absolute_url; start_batch python:(paging_current_page-1)*paging_records_page"
		tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">&lt;&lt; Previous</a></span>
		<span	tal:repeat="page paging_pages">
			<a	class="paging-link-off"
				tal:condition="python:paging_current_page==page"
				tal:content="python:page+1" />
			<a	tal:condition="python:paging_current_page!=page"
				tal:define="url here/absolute_url; start_batch python:paging_records_page*page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}"
				tal:content="python:page+1" />
		</span>
		<span	tal:condition="python:paging_next!=-1">&nbsp;&nbsp;
			<a	tal:define="url here/absolute_url; start_batch python:(paging_current_page+1)*paging_records_page"
				tal:attributes="href string:${url}?start=${start_batch}&${page_search_querystring}">Next &gt;&gt;</a>
		</span>
</p>
</tal:block>

<p>
	<a href="index_rdf" target="_blank"><img src="/misc_/NaayaCore/xml.png" alt="Syndication (XML)" border="0"  i18n:attributes="alt" /></a>

	<tal:block define="fld_url python:here.utUrlEncode(here.absolute_url(1))">
	<a tal:attributes="href string:${here/absolute_url}/generate_pdf?url=${fld_url}&amp;lang=${here/gl_get_selected_language}" target="_blank"><img tal:attributes="src string:${here/getSitePath}/images/pdf.gif" alt="PDF View" border="0"  i18n:attributes="alt" /></a>
	</tal:block>
</p>

<p tal:condition="python:request.AUTHENTICATED_USER.getUserName() == 'Anonymous User'">
	[<a tal:attributes="href string:${here/absolute_url}/requestrole_html" i18n:translate="">Create an account for content contributions</a>]
</p>
</div>
<span tal:replace="structure here/standard_html_footer"/>"""

        errors = []
        site = self.getSite()
        formstool_ob = site.getFormsTool()
        formstool_ob._getOb('semthematicdir_index').pt_edit(text=thematic_dir_index, content_type='')
        formstool_ob._getOb('site_admin_messages').pt_edit(text=site_admin_messages, content_type='')
        formstool_ob._getOb('site_admin_centre').pt_edit(text=site_admin_centre, content_type='')

        layouttool_ob = site.getLayoutTool()
        layouttool_ob.semide._getOb('site_header').pt_edit(text=semide_site_header, content_type='')


        try:
            iniatives_ob = site._getOb('initiatives')
            database = iniatives_ob._getOb('fol060732')
            database._getOb('index').pt_edit(text=semide_initiative_database_index, content_type='')
        except:
            errors.append("semide_initiative_database_index")

#        try:
#            iniatives_ob = site._getOb('initiatives')
#            medeeau_ob = iniatives_ob._getOb('medaeau')
#            projects = medeeau_ob._getOb('fol719001')
#            projects._getOb('index').pt_edit(text=semide_initiatives_medaeau_projects, content_type='')
#        except:
#            print "semide_initiatives_medaeau_projects"
#
#        try:
#            iniatives_ob = site._getOb('initiatives')
#            incomed_ob = iniatives_ob._getOb('incomed')
#            projects = incomed_ob._getOb('fol871304')
#            projects._getOb('index').pt_edit(text=semide_initiatives_incomed_projects, content_type='')
#        except:
#            print "semide_initiatives_incomed_projects"
#
#        try:
#            iniatives_ob = site._getOb('initiatives')
#            life = iniatives_ob._getOb('life')
#            projects = life._getOb('fol871304')
#            projects._getOb('index').pt_edit(text=semide_initiatives_life_projects, content_type='')
#        except:
#            print "semide_initiatives_life_projects"

        try:
            thematicdirs = site._getOb('thematicdirs')
            news = thematicdirs._getOb('news')
            news._getOb('index').pt_edit(text=semide_thematicdirs_news, content_type='')
        except:
            errors.append("semide_thematicdirs_news")

        try:
            thematicdirs = site._getOb('thematicdirs')
            events = thematicdirs._getOb('events')
            events._getOb('index').pt_edit(text=semide_thematicdirs_events, content_type='')
        except:
            errors.append("semide_thematicdirs_events")

        from Products.NaayaContent import METATYPE_NYCOUNTRY
        for r in site.getCatalogedObjects(meta_type=METATYPE_NYCOUNTRY):
            try:
                project_water = r._getOb('project_water')
                project_water._getOb('index').pt_edit(text=project_water_index, content_type='')
            except:
                errors.append("country --> %s" % r.absolute_url(0))

        if errors:
            return "some errors found %s" % '<br />'.join(errors)
        else:
            return "update status: ok"

InitializeClass(SemideVersions)
