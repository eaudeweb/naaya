Naaya EnviroWindowsGoogleSearchInterface

CODE TO INTEGRATE INTO folder_index (usually just after this line: <span tal:replace="structure here/menusubmissions" />):

	<tal:block tal:condition="here/checkPermissionPublishObjects" tal:define="googlesearch python:here.getObjectById('GoogleSearch')">
		<table border="0" cellspacing="2" cellpadding="2" tal:condition="python:googlesearch is not None">
			<tr>
				<td>Google Search:</td>
				<td><a href="./GoogleSearch/index_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/search.jpg" border="0" alt="Manual search" title="Manual search form" /></a></td>
				<td><a href="./GoogleSearch/cache_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/temp_basket.jpg" border="0" alt="Temporary basket" title="Temporary basket" /></a></td>
				<tal:block tal:condition="googlesearch/automaticModeEnabled">
				<td>Automatic:</td>
				<td><a href="./GoogleSearch/automatic_properties_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/properties.jpg" border="0" alt="Properties" title="Configure properties for the automatic mode" /></a></td>
				<td><a href="./GoogleSearch/automatic_index_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/search.jpg" border="0" alt="Configure" title="Configure automatic search" /></a></td>
				<td><a href="./GoogleSearch/automatic_log_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/log.jpg" border="0" alt="Activities log" title="Activities log" /></a></td>
				</tal:block>
				<td><a href="./GoogleSearch/help_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/help.gif" border="0" alt="Help" title="Help" /></a></td>
			</tr>
		</table>
		<table border="0" cellspacing="2" cellpadding="2" tal:condition="python:googlesearch is None">
			<tr>
				<td>Google Search:</td>
				<td><a href="addEWGoogleSearchInterface_html"><img src="misc_/EnviroWindowsGoogleSearchInterface/search.jpg" border="0" alt="Add Google Search Interface" title="Add Google Search Interface" /></a></td>
			</tr>
		</table>
	</tal:block>
