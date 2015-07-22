LayoutTool

20080919 - Cristian Romanescu:

Forms are now served from disk and the system works as follows:

When a new site is created, forms are loaded (form skel.xml) following the old logic:
1) Forms from Naaya skel.xml (forms tool and pluggable content types)
2) Forms for specific site (SMAP, EnviroWindows) overrides existing Naaya forms and adds their new forms
3) Skins are also loaded as 1) and 2)

Skins and Forms are the only objects which may contain Template objects (subject to disk serving)


Now the content is served from disk unless form (Template) is marked as customized, case when is served from ZODB.

ZMI:
From the ZMI a form (Template) may be customized, starting to serve its content from ZODB and ignore file content on disk.
Also a new tab was added called 'View modifications' which shows the two versions (file, ZODB) for comparison.
Editing and saving a form from the ZMI, automatically marks it as customized and serves it from ZODB
There is also an option to 'rollback' the customization and serve it again from disk


Technical stuff:
There were two new fields added to the Template object (path and customized with their correspondent setters and getters).
'path' field keeps track of the original absolute path of file where the form was loaded from
'customized' keeps track of the form state. If customized is True, then froms is served from ZODB, from file otherwise


Further optimizations:
1) While a new NySite is created, forms content is still copied into ZODB even if is not used until a form is 'customized'.
An optimization would be to prevent forms to be loaded while new site is created and implies that content to be copied from file in ZODB while starting form customization.


On existing site the following NaayaUpdate must be run: update_forms_to_disk.py