Portal translations
===================

Naaya portals are multilingual in terms of interface, content, search and syndication. Initially, the only available languages is English. 
*Managers* can easily define additional languages in which the portal can be translated by using the Zope Management Interface. Add/remove languages operations can be done by accessing the *Languages* tab of the *portal_properties* object from the root of each Naaya portal. 
Also from here, the default language of the portal can be set. Once a language is added or deleted, this is immediately reflected around the portal interface and content. 
All Naaya portal pages are encoded in *UTF-8(Unicode)*, which means that all characters and signs from any language are supported. 

*The language negotiation process*

Here's the full language negotiation process:
	1. *Navigation language* (end user selection) 
	2. *Preferred local language* (client's browser or operating system) 
	3. Default portal language

When an end user opens a portal page for the first time, a localization process takes place and the navigation language is set. If any match is found between the list of available languages for the portal and the languages in the browsers preferences, that language is set for the navigation language by default. If more language matches are found, then the first one in the settings of the browser takes precedence.
The end user can manually select the navigation language at any time and from any portal page from the list of available languages. This will overrule all other settings done automatically by the system.

*Multilingual interface*

All labels, explanatory messages, lists of links and their descriptions, the portlets (aside from the static ones) and other texts that appear in the user interface can be translated by specialised people in any of the available languages using the *Translate messages* form available in the administration centre. 
The translation centre for the interface lists the messages marked for translation in the portal and users can translate them individually. To ease the translation process, when a message is translated into a language, an OK sign will appear next to it in the language column. A message search is available which will narrow down the list of messages to those that contain a certain text. Users can sort the list of messages, both ascending and descending: alphabetically or by translation status in a certain language.  
Some of the messages contain HTML tags because splitting the texts around the tags would mean taking some phrases out of their context and therefore losing their meaning. All HTML tags MUST NOT be changed during the translation process. 

Since the number of messages to translate is high, an export can be made in .PO, .XLIFF or .CSV formats, the texts translated using external tools (e.g. text editors, specific translation tools) and imported back into the portal. Such operation can be made from the *Import/Export messages* tab of the Translate messages centre. 
The PO file is a simple text file which will be downloaded with texts in English and the target language in which the messages have to be translated, while the XLIFF file is XML and it's particularly useful when the translators use desktop programs (that understand such formats) that know to navigate among the messages, to suggest translations, search messages, escape HTML tags, etc. 



Translating messages with several versions in the target language
-----------------------------------------------------------------
If a message in english has several translations in the target language (ex. "type" in english can be translated by "Typ" and by "eingeben" in German, when it is used as a noun and as a verb, respectively), the two entries should receive both a message ID and a message value in the ZPT:

    <p i18n:translate="Type (translation tip: used as a noun)">Type</p>
    <p i18n:translate="Type (translation tip: used as a verb)">Type</p>

The value will be displayed in the english version and the ID will help the translater understand how he should... translate.


Bulk-updating translations in several portals
---------------------------------------------

There is a handy update tool in *Naaya Updates* called *Update Translations*
that helps you insert or update translations in more portals at once.

You need to provide a .PO file with your translations - it doesn't need to contain
all the messages in your portal, but only the ones you want to change. If a
message lacks translation, it will be ignored. Also specify the language to insert
translations in, as .PO files do not contain language information.
If a portal you selected does not have that specific language code installed, it
will be skipped. Every event in the update is logged.

Next, you will find the list of portals available in your Zope instance, as you
were probably accoustomed to in other update procedures. Simply check the portals
you want to be patched with your list of translations.

Take note that the .PO file needs to be encoded with UTF-8 charset. If you have
non-latin characters in your translations, please make sure you set
`management_page_charset` string property in your Zope root with 'utf-8' value;
elsewise, your update will output error when trying to display the logs of the
update.
