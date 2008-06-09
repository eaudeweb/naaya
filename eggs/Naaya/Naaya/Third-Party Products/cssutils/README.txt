========================================================
cssutils - CSS Cascading Style Sheets library for Python
========================================================
Copyright (C) 2004 Christof Hoeke
Published under the LGPL, see http://cthedot.de/cssutils/license.html

A Python package to parse and build CSS Cascading Style Sheets.
Partly implements the DOM Level 2 CSS interfaces
(http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/css.html).
Additional some cssutils only convenience and (hopefully) more pythonic methods are integrated.

Uses xml.dom.DOMException and subclasses so may need PyXML.
Tested with Python 2.3.3 on Windows XP with PyXML 0.8.3 installed.

Please visit http://cthedot.de/cssutils/ for full details and updates.

============
installation
============
Expand the zipfile and from a command line use
    >python setup.py install
to install.

============
  examples
============
See the website for implementation details and examples or see the DOM Level 2 CSS specification. 

The main (and mostly stable) modules are
    cssutils.cssparser
    use class cssparser.CSSParser to parse CSS StyleSheets
        
    cssutils.cssbuilder
    use to build new CSS StyleSheets


============
    todo
============
UnknownRule:
    - parser needs to use it instead of dumping unknown atrules!
lexer
	- preserve whitespace in comments
ALL
	- more UnitTests	
		- MediaRule
        - __init__ !!!
	- comments?
	- readonly?
StyleRule
	- cssText setting 
	- parsing of selectors
ImportRule
	- @import load and parse href
	- ownerNode, ParentNode attribs
PageRule
	- properties
	- format of properties!
docs
custom serializer?

============
  changes
============
0.51 - 040412
	!cssnormalizer does not work in this version - on hold for 1.0

	API CHANGES
	cssrule.SimpleAtRule DEPRECATED and empty
	cssmediarule.MediaRule init param "medias" renamed to "media"
	use subclasses of CSSRule (CharsetRule, ImportRule,
	FontFaceRule or PageRule) instead
	StyleRule constructor can be called with arguments (again...)
	Comment attribute "comment" renamed to "text"

	implemented at least partly almost all DOM Level 2 CSS interfaces now
	so the API should be more stable from now on
	
	new statemachine and lexer helper classes for parsing
	complete rewrite of CSSParser
	CSSParser and lexer put all error messages in a log now
	you might give your own log for messages
	CSSParser might be configured just to log errors or to raise
	xml.dom.DOMExceptions when finding an error

0.41 - 040328
	!cssnormalizer does not work in this version - on hold for 1.0

	API CHANGES
	StyleSheet.getRules() returns a RuleList now
	class Selector removed, integrated into Rules now
	
	moved most Classes to own module
		StyleSheet, StyleRule, MediaRule, ...

0.4a - 040321
	!cssnormalizer does not work in this version
	
	API CHANGES:
	cssbuilder.RuleList subclasses list
	cssbuilder.Selector moved to cssrules
	attribute style of class StyleRule 
		made private (_style)
	removed StyleRule.clearStyleDeclaration 
	attribute selectorlist of class Selector
		renamed to _selectors and made private

	NEW:
	MediaList class	

	moved tests to directory test

	made a dist package complete with setup.py
		
		
0.31 - 040320
	!cssnormalizer does not work in this version

	API CHANGES:
	StyleDeclaration.addProperty is now DEPRECATED
	use StyleDeclaration.setProperty instead

	removed CSSParser.pprint(). use CSSParser.getStyleSheet().pprint() instead
		(a StyleSheet object had a pprint method anyway)

	replaced cssutils own exceptions with standard xml.dom.DOMException 
		and subclasses
		!catch these exceptions instead of CSSException or CSSParserException

	moved internal lists (e.g. StyleSheet.nodes list) to private vars
		StyleSheet._nodes
		!please use methods instead of implementation details
	
	
	removed cssexception module
	removed csscomment module, classes now directly in cssutils

	more unittests, start with python cssutils/_test.py
	
	more docs

	integrated patches by Cory Dodt for SGML comments and Declaration additions
	added some w3c DOM methods 


0.3b - 040216
	severe API changes
	renamed some classes to (almost) DOM names 
	   the CSS prefix of DOM names is ommited though
	renamed are
		Stylesheet TO StyleSheet
		Rule TO StyleRule
		AtMediaRule TO MediaRule
		Declaration TO StyleDeclaration
	the according methods are renamed as well
	
	class hierarchy is changed as well, please see the example
	
	classes are organized in new modules
	

0.241 - 040214	
	legal stuff: added licensing information 
	no files released

0.24 - 040111	
	split classes in modules, has to be cleaned up again

0.24b - 040106	
	cleaned up cssbuilder
		- Comment now may only contain text
			and no comment end delimiter. 
			(before it had to be a complete css 
			comment	including delimiters)
		- AtMediaRule revised completely
			validates given media types
			new method: addMediaType(media_type)
	cssparser updated to new cssbuilder interface and logic
	started unittests (v0.0.0.1..., not included yet)
	
	
0.23 - 031228	
	new CSSNormalizer.normalizeDeclarationOrder(stylesheet)
	cssbuilder:
		added methods needed by CSSNormalizer
	CSSParser.parse bugfix


0.22 - 031226	
	CSSParser: 
			added \n for a declaration ending in addition to ; and }
	cssbuilder:
		docstrings added for @import and @charset
		support build of a selector list in a rule


0.21 - 031226	
	cleaned up docstrings and added version information

0.20 - 031224	
	complete rewrite with combination of parser and builder classes

0.10 - 031221	
	first version to try if i can bring it to work at all
	only a prettyprinter included, no builder

