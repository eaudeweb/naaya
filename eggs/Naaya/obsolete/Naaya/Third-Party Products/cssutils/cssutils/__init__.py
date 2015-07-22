"""
cssutils - CSS Cascading Style Sheets library for Python

    Copyright (C) 2004 Christof Hoeke

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

A Python package to parse and build CSS Cascading Style Sheets.
Partly implements the DOM Level 2 CSS interfaces
(http://www.w3.org/TR/2000/REC-DOM-Level-2-Style-20001113/css.html).
Additional some cssutils only convenience and (hopefully) more pythonic methods are integrated.

Uses xml.dom.DOMException and subclasses so may need PyXML.
Tested with Python 2.3.3 on Windows XP with PyXML 0.8.3 installed.

Please visit http://cthedot.de/cssutils/ for full details and updates.

The main modules are
    cssutils.cssparser
    use class cssparser.CSSParser to parse CSS StyleSheets
        
    cssutils.cssbuilder
        use to build new CSS StyleSheets
"""
__version__ = '0.51'

import xml.dom


class Commentable(object):
    "a base class for all classes with possible comments"

    def addComment(self, comment):
        if isinstance(comment, str):
            comment = Comment(comment)
        self._nodes.append(comment)


class Comment(object):
    "a CSS comment holder"
    # CONSTANT
    type = 0    # TODO cssrule.CSSRule.UNKNOWN_RULE!!!

    def __init__(self, text):
        if text.find('/*') != -1 or text.find('*/') != -1:
            raise xml.dom.SyntaxErr('A comment must not contain "/*" or "*/"')
        self.text = text

    # fget
    def getFormatted(self, indent=4, offset=0):
        return '%s/* %s */' % (offset*' ', self.text)
    # fset
    def _getCssText(self):
        return self.text
    # property
    cssText = property(_getCssText, doc='Textual representation of this comment')
