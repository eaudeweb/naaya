"""
contains DOM Level 2 CSSFontFaceRule implementation class.

TODO
    cssText: fset not implemented yet
"""
__version__ = '0.51'

import exceptions 
import xml.dom
import cssrule


class FontFaceRule(cssrule.CSSRule):
    """
    represents a @font-face rule in a CSS style sheet. 
    """
    type = cssrule.CSSRule.FONT_FACE_RULE # CONSTANT

    def __init__(self, style=None, readonly=False):
        self._readonly = False      
        self._setStyle(style)
        self._readonly = readonly
         
    # fget
    def _getStyle(self):
        return self._style
    # fset
    def _setStyle(self, style):
        if (self._readonly):
            raise xml.dom.NoModificationAllowedErr(
                'FontFaceRule is readonly')
        self._style = style
    # property - NORMALLY READONLY!
    style = property(_getStyle, _setStyle,
                doc="(DOM attribute) The declaration-block of this rule.")

    # fget
    def getFormatted(self, indent=4, offset=0):
        "returns inherited property cssText or the empty string"
        offsetspace = offset * u' '
        indentspace = indent * u' '
        out = []
        if self._style:
            out.append(offsetspace + u'@font-face {')
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
        if (self._readonly):
            raise xml.dom.NoModificationAllowedErr(
                'FontFaceRule is readonly')
        raise exceptions.NotImplementedError()
    # property
    cssText = property(getFormatted, _setCssText,
                       doc="(DOM attribute) The parsable textual\
                       representation of the rule.")
