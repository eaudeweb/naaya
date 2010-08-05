"""
contains DOM Level 2 CSSPageRule implementation class.

TODO
    cssText: fset not implemented yet
    special properties of @page! and format of these
"""
__version__ = '0.51'

import exceptions 
import xml.dom
import cssrule


class PageRule(cssrule.CSSRule):
    """
    represents a @page rule within a CSS style sheet. The @page rule is
    used to specify the dimensions, orientation, margins, etc. of a page
    box for paged media.
    """
    # CONSTANT
    type = cssrule.CSSRule.PAGE_RULE 

    def __init__(self, selectorText=None, style=None, readonly=False):
        self._readonly = False
        self._setSelectorText(selectorText)
        self._setStyle(style)
        self._readonly = readonly
         
    # fget
    def _getStyle(self):
        return self._style
    # fset - NORMALLY READONLY
    def _setStyle(self, style):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr('PageRule is readonly')
        self._style = style
    # property 
    style = property(_getStyle, _setStyle,
                doc="(DOM attribute) The declaration-block of this rule.")

    # fget
    def getFormatted(self, indent=4, offset=0):
        "returns inherited property cssText prettyprinted"
        offsetspace = offset * u' '
        indentspace = indent * u' '
        out = []
        if self._style:
            sel = self.selectorText
            if sel:
                out.append(offsetspace + u'@page ' + sel + u' {')
            else:
                out.append(offsetspace + u'@page {')
            out.append(self._style.getFormatted(indent, offset))
            out.append(offsetspace + indentspace + u'}')
            return '\n'.join(out)
        else:
            return u''
    # fset
    def _setCssText(self, cssText):
        """
        NOT IMPLEMENTED YET
        Exceptions on setting
            DOMException
            SYNTAX_ERR: Raised if the specified CSS string value has a
                syntax error and is unparsable.
            INVALID_MODIFICATION_ERR: Raised if the specified CSS string
                value represents a different type of rule than the current
                one.
            HIERARCHY_REQUEST_ERR: Raised if the rule cannot be inserted at
                this point in the style sheet.
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr('PageRule is readonly')
        raise exceptions.NotImplementedError()
    # property
    cssText = property(getFormatted, _setCssText,
                       doc="(DOM attribute) The parsable textual\
                       representation of the rule.")

    # fget
    def _getSelectorText(self):
        return u', '.join(self._selectors)
    # fset
    def _setSelectorText(self, selectorText):
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr('PageRule is readonly')
        # TODO: parse
        # :left, :right or :first?
        if False: 
            raise xml.dom.SyntaxErr('Empty text for selectorText given.')
        # empty current
        self._selectors = []
        if selectorText:
            for s in selectorText.split(u','):
                self._selectors.append(s.strip())
    # property
    selectorText = property(_getSelectorText, _setSelectorText,
                            doc="(DOM attribute) The parsable textual\
                            representation of the page selector for the\
                            rule.")

