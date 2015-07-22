EditorTool

Editor tool is a widget used to create with rich content with text 
formatting, image, multimedia etc.

Known issues:
 * Google Chrome 3.0.195.33: Cliking image in editor doesn't select it
 * Safari 4.0.3 (531.9.1): Cliking image in editor doesn't select it

20091116:
	cristiroma: Started update to v2.
	This improvement updated the underlying component TinyMCE to version 3.
	I have removed all the naaya plugin code and patched the advimage plugin 
	to open my own template. This decision was taken having in mind the fact
	that creating custom plugins is difficult (advimage is not only native 
	to tinymce but also upper code also creates menu entries dependant 
	on this plugin). So I have removed all the code from the plugin and kept
	the custom actions that open my own dialogs with their own code.
	The advlink plugin was patched too to support new link selection system.
	
	WARNING! Please keep in mind that updating the TinyMCE requires to update
	the patched advimage and advlink plugins too. Put the patched plugins into
	the new archive first.

	
	