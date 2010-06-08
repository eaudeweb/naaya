#data=''

EVENT_ADD_ORIG = """</tal:block>

</tal:block>"""
EVENT_ADD_UPD = """<div class="field">
	<img tal:attributes="src string:${here/getSitePath}/getCaptcha" alt="" />
</div>
<div class="field">
	<label for="contact_word"><span i18n:translate="" tal:omit-tag="">Word verification</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(kind, 'contact_word')" class="mandatory_field"> *</span></label>
	<input type="text" name="contact_word" size="50" id="contact_word" value="" />(required)<br />
	<em i18n:translate="">please type the word you see in the above picture.</em>
</div>
</tal:block>

</tal:block>"""

STORY_ADD_ORIG1 = """<form name="frmAdd" method="post" tal:attributes="action string:${here/absolute_url}/process_add">"""
STORY_ADD_UPD1 = """<form name="frmAdd" method="post" tal:attributes="action string:${here/absolute_url}/process_add" enctype="multipart/form-data">"""

STORY_ADD_ORIG2 = """<div class="field">
	<label for="resourceurl"><span i18n:translate="" tal:omit-tag="">Concerned URL"""
STORY_ADD_UPD2 = """<div class="field">
	<label for="frontpicture"><span i18n:translate="" tal:omit-tag="">Front page picture</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'frontpicture')" class="mandatory_field"> *</span></label>
	<input type="file" id="frontpicture" name="frontpicture" />
	<span tal:condition="python:test(here.getSession('frontpicture', ''))" tal:content="python:here.getSession('frontpicture', '')" />
</div>

<div class="field">
	<label for="resourceurl"><span i18n:translate="" tal:omit-tag="">Concerned URL"""

POINTER_ADD_ORIG = """<tal:block metal:use-macro="python:here.getFormsTool().site_macro_add.macros['page']">"""

POINTER_ADD_UPD = """<span tal:define="global t string:pointer" tal:omit-tag="" />
<tal:block metal:use-macro="python:here.getFormsTool().site_macro_add.macros['page']">"""

MEDIAFILE_ADD_ORIG = """<tal:block metal:use-macro="python:here.getFormsTool().site_macro_add.macros['page']">"""

MEDIAFILE_ADD_UPD = """<span tal:define="global t string:pointer" tal:omit-tag="" />
<tal:block metal:use-macro="python:here.getFormsTool().site_macro_add.macros['page']">"""

MEDIAFILE_EDIT = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	tal:attributes="xml:lang here/gl_get_selected_language; lang here/gl_get_selected_language"
	tal:define="site_url here/getSitePath">

<tal:block metal:use-macro="python:here.getFormsTool().admin_macros.macros['head']" />
<body id="edit">
<div id="wrap">
<tal:block metal:use-macro="python:here.getFormsTool().admin_macros.macros['header']" />


<div id="content"><div id="adminTitle">
<h1 i18n:translate="">Edit Media File</h1>
</div>
				<a name="contentstart" id="contentstart"></a>
				<div id="content_info">
					<span tal:replace="structure here/messages_box"/>

<tal:block tal:condition="python:(not here.hasVersion()) or (here.hasVersion() and here.isVersionAuthor())">
<tal:block define="languages here/get_languages_mapping;
					curr_lang python:request.get('lang', None) or here.gl_get_selected_language()">

<div class="version_box" tal:condition="here/hasVersion">
	<span i18n:translate="" tal:omit-tag="">
		<strong>You are working on a version of this item.</strong> In order to save the work done in the version and make it accessible to all end users, click on the <strong>Commit</strong> button. To permanently discard the work done in the version, click on the <strong>Discard</strong> button.
	</span>
	<br /><br />
	<form style="display: inline;" action="commitVersion"><input type="submit" value="Commit" i18n:attributes="value" /></form>
	<form style="display: inline;" action="discardVersion"><input type="submit" value="Discard" i18n:attributes="value" /></form>
</div>

<div class="floated-buttons"><span class="buttons"><a tal:attributes="href here/absolute_url" i18n:translate="">Back to index</a></span></div>

<p i18n:translate="">
	Change the properties in the form below and click <strong>Save changes</strong>. Fields marked with <span class="mandatory_field">*</span> are mandatory.
</p>

<script type="text/javascript">
<!--
function fPick(glossary_url)
{
	var wnd = window.open(glossary_url, "pickkeyword", "height=400,width=500,status=no,resizable=no,toolbar=no,menubar=no,location=no,scrollbars=yes");
	wnd.focus();
}

function fSet(ctrl, value)
{
	var frm = document.frmEdit;
	var items = frm[ctrl + ':utf8:ustring'];
	if (value != '')
	{
		if (items.value == '')
			items.value = value;
		else
			items.value = items.value + ', ' + value;
	}
}

function check_srt(file_obj) {
  var ext = file_obj.value;
  ext = ext.substring(ext.length - 3, ext.length);
  ext = ext.toLowerCase();
  if(ext != 'srt') {
    file_obj.value = "";
    alert('You selected a .' + ext +
          ' file. Please select a .srt file instead!');
  }
}

function displayToolTips(tips_id, style){
  var tips = document.getElementById(tips_id);
  tips.style.display = style;
}
// -->
</script>
<div id="formEdit">
<ul class="translate top">
<tal:block tal:repeat="language languages">
<li tal:condition="python:language['code'] == curr_lang" class="current" tal:attributes="class string:curr_lang ${language/code}">
<a tal:attributes="href string:?lang=${language/code}; title python:language['name']"
	tal:content="python:language['name']" /></li>
<li tal:condition="python:language['code'] != curr_lang" tal:attributes="class language/code"><a
	tal:attributes="href string:?lang=${language/code}; title python:language['name']"
	tal:content="python:language['name']" /></li>
</tal:block>
</ul>

<div class="version_box" tal:condition="here/hasVersion">
	<span i18n:translate="" tal:omit-tag="">
		<strong>You are working on a version of this item.</strong> In order to save the work done in the version and make it accessible to all end users, click on the <strong>Commit</strong> button. To permanently discard the work done in the version, click on the <strong>Discard</strong> button.
	</span>
	<br /><br />
	<form style="display: inline;" action="commitVersion"><input type="submit" value="Commit" i18n:attributes="value" /></form>
	<form style="display: inline;" action="discardVersion"><input type="submit" value="Discard" i18n:attributes="value" /></form>
</div>

<form method="post" action="saveProperties" name="frmEdit" id="frmEdit" 
  enctype="multipart/form-data">

<div class="field">
	<label for="title"><span i18n:translate="" tal:omit-tag="">Title</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'title')" class="mandatory_field"> *</span></label>
	<input type="text" name="title:utf8:ustring" id="title" size="50" tal:attributes="value python:here.getSession('title', here.getVersionLocalProperty('title', curr_lang))" />
</div>
<div class="field">
	<label for="description"><span i18n:translate="" tal:omit-tag="">Description</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'description')" class="mandatory_field"> *</span></label>
	<span tal:replace="structure python:here.get_wysiwyg_widget('description:utf8:ustring', here.getSession('description', here.getVersionLocalProperty('description', curr_lang)))" />
</div>
<div class="field">

<table>
  <tr><td>
    <label for="subtitle">
      <span i18n:translate="" tal:omit-tag="">Subtitle</span>
      <span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'subtitle')" class="mandatory_field"> *</span>
   </label>
   <p i18n:translate=""><strong>Tip:</strong> You can edit subtitle in text area below or upload it from a local file.</p>
   <textarea 
     onfocus="javascript:displayToolTips('subtitle_tips', 'block')"
     onblur="javascript:displayToolTips('subtitle_tips', 'none')"
     id="subtitle" name="subtitle" rows="15" cols="70"
     tal:content="python:here.getSession('subtitle', here.getVersionLocalProperty('subtitle', curr_lang))"></textarea>
  </td><td>
  <div id="subtitle_tips" style="display: none" class="toolTips">
    <pre>
Example:

  1
  00:00:20,000 --> 00:00:24,400
  In connection with a dramatic increase
  in crime in certain neighbourhoods,

  2
  00:00:24,600 --> 00:00:27,800
  The government is implementing a new policy...
    </pre>
  </div>
  </td></tr>
</table>

    <label for="subtitle_file">
	  <span i18n:translate="" tal:omit-tag="">Upload subtitle (.srt)</span>
	</label>
    <input type="file" onchange="javascript:check_srt(this);" size="50"
	  name="subtitle_file" id="subtitle_file" value=""/>
</div>
<div class="field" tal:define="coverage_glossary here/get_coverage_glossary">
	<label for="coverage"><span i18n:translate="" tal:omit-tag="">Geographical coverage</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'coverage')" class="mandatory_field"> *</span></label>
	<tal:block tal:condition="python:coverage_glossary is None">
		<p i18n:translate=""><strong>Tip:</strong> in order to specify more values, separate them by commas</p>
	</tal:block>
	<tal:block tal:condition="python:coverage_glossary is not None">
		<p i18n:translate=""><strong>Tip:</strong> you can type free text in the field below or pick words from the list. In order to specify more values, separate them by commas.</p>
	</tal:block>
	<input type="text" name="coverage:utf8:ustring" id="coverage" size="50" tal:attributes="value python:here.getSession('coverage', here.getVersionLocalProperty('coverage', curr_lang))" />
	<tal:block tal:condition="python:coverage_glossary is not None">
		<label for="pick-coverage" class="invisible" i18n:translate="">Pick coverage</label><input type="button" value="Pick" id="pick-coverage" tal:attributes="onclick string:javascript:fPick('${coverage_glossary/absolute_url}/GlossMap_html?ctrl=coverage&amp;lang=${curr_lang}');" />
	</tal:block>
</div>
<div class="field" tal:define="keywords_glossary here/get_keywords_glossary">
	<label for="keywords"><span i18n:translate="" tal:omit-tag="">Keywords</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'keywords')" class="mandatory_field"> *</span></label>
	<tal:block tal:condition="python:keywords_glossary is not None">
		<p><strong>Tip:</strong> you can type free text in the field below or pick words from the glossary</p>
	</tal:block>
	<input type="text" name="keywords:utf8:ustring" id="keywords" size="50" tal:attributes="value python:here.getSession('keywords', here.getVersionLocalProperty('keywords', curr_lang))" />
	<tal:block tal:condition="python:keywords_glossary is not None">
		<label for="pick-keywords" class="invisible">Pick keywords</label><input type="button" value="Pick" id="pick-keywords" tal:attributes="onclick string:javascript:fPick('${keywords_glossary/absolute_url}/GlossMap_html?ctrl=keywords&amp;lang=${curr_lang}');" />
	</tal:block>
</div>
<div class="field">
	<label for="sortorder"><span i18n:translate="" tal:omit-tag="">Sort order</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'sortorder')" class="mandatory_field"> *</span></label>
	<input type="text" name="sortorder" id="sortorder" size="2" tal:attributes="value python:here.getSession('sortorder', here.getVersionProperty('sortorder'))" />
</div>
<div class="field">
	<label for="releasedate"><span i18n:translate="" tal:omit-tag="">Release date (<em>dd/mm/yyyy</em>)</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'releasedate')" class="mandatory_field"> *</span></label>
	<input type="text" name="releasedate" id="releasedate" size="20" tal:attributes="value python:here.getSession('releasedate', here.utConvertDateTimeObjToString(here.getVersionProperty('releasedate')))" />
</div>
<div class="field">
	<label for="discussion"><span i18n:translate="" tal:omit-tag="">Open for comments</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'discussion')" class="mandatory_field"> *</span></label>
	<input type="checkbox" name="discussion" id="discussion" tal:attributes="checked python:test(here.getSession('discussion', here.discussion), 'checked', '')" />
</div>
<div class="field" tal:repeat="record python:here.getDynamicPropertiesTool().getDynamicProperties(here.meta_type)">
	<label tal:attributes="for record/id" i18n:translate=""><span tal:replace="record/name" /></label>
	<tal:block tal:content="structure python:record.render(here.getPropertyValue(record.id, curr_lang))">dynamic html control</tal:block>
</div>
<div class="field">
	<input type="hidden" name="lang" tal:attributes="value curr_lang" />
	<input type="submit" value="Save changes" i18:attributes="value" />
</div>

<div class="translate"><span i18n:translate="" tal:omit-tag="">Translate in</span>
<tal:block tal:repeat="language languages">
<strong tal:condition="python:language['code'] == curr_lang">
<a class="current" tal:attributes="href string:?lang=${language/code}; title python:language['name']"
	tal:content="python:language['name']" /></strong>
<a tal:condition="python:language['code'] != curr_lang"
	tal:attributes="href string:?lang=${language/code}; title python:language['name']"
	tal:content="python:language['name']" />
</tal:block>
</div>

</form>

<br />

<form method="post" action="saveUpload" enctype="multipart/form-data">
<div class="field">
	<label><span i18n:translate="" tal:omit-tag="">Upload media file</span><span tal:condition="python:here.get_pluggable_item_property_mandatory(here.meta_type, 'file')" class="mandatory_field"> *</span></label>
</div>
<div class="field-inline">
	<input type="file" name="file" id="file" size="40" value="" />
	<label for="file" class="invisible" i18n:translate="">(local computer or network)</label>
</div>
<div class="field">
	<input type="submit" value="Upload" i18n:attributes="value" />
</div>
</form>

</tal:block>
</tal:block>

<tal:block tal:condition="python:here.hasVersion() and (not here.isVersionAuthor())">
	<strong i18n:translate="">This object is checked out for editing by another user.</strong>
</tal:block>

<div class="floated-buttons bottom"><a tal:attributes="href here/absolute_url" i18n:translate="">Back to index</a></div>
<span tal:content="python:here.del_pluggable_item_session(here.meta_type)" tal:omit-tag="" />
<tal:block metal:use-macro="python:here.getFormsTool().admin_macros.macros['footer']" />
</div>
</body>
</html>
"""

if data == 'EVENT_ADD_ORIG':
  return EVENT_ADD_ORIG
elif data == 'EVENT_ADD_UPD':
  return EVENT_ADD_UPD
elif data == 'STORY_ADD_ORIG1':
  return STORY_ADD_ORIG1
elif data == 'STORY_ADD_UPD1':
  return STORY_ADD_UPD1
elif data == 'STORY_ADD_ORIG2':
  return STORY_ADD_ORIG2
elif data == 'STORY_ADD_UPD2':
  return STORY_ADD_UPD2
elif data == 'POINTER_ADD_ORIG':
  return POINTER_ADD_ORIG
elif data == 'POINTER_ADD_UPD':
  return POINTER_ADD_UPD
elif data == 'MEDIAFILE_ADD_ORIG':
  return MEDIAFILE_ADD_ORIG
elif data == 'MEDIAFILE_ADD_UPD':
  return MEDIAFILE_ADD_UPD
elif data == 'MEDIAFILE_EDIT':
  return MEDIAFILE_EDIT
