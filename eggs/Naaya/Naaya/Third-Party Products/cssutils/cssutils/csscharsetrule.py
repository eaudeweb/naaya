"""
contains DOM Level 2 CSSCharsetRule implementation class.

TODO
    comment handling
    encoding: fset: SYNTAX_ERR Raised if the specified encoding value has a
                        syntax error and is unparsable.
    cssText: fset not implemented yet
"""
__version__ = '0.51'

import exceptions 
import xml.dom
import cssrule


class CharsetRule(cssrule.CSSRule):
    """
    represents a @charset rule in a CSS style sheet. 
    """
    type = cssrule.CSSRule.CHARSET_RULE # CONSTANT

    def __init__(self, encoding='', readonly=False):
        """
        allows setting of encoding in constructor only
        """
        self._readonly = False
        self._setEncoding(encoding)
        self._readonly = readonly

    # fget
    def _getEncoding(self):
        return (self._encoding)
    # fset
    def _setEncoding(self, encoding):
        if (self._readonly):
            raise xml.dom.NoModificationAllowedErr(
                'CharsetRule is readonly')
        self._encoding = encoding
    # property
    encoding = property(_getEncoding, _setEncoding,
        doc="(DOM)The encoding information used in this @charset rule.")

    # fget
    def getFormatted(self, indent=4, offset=0):
        "returns inherited property cssText prettyprinted"
        if self._encoding:
            text = u'@charset "%s";' % self._encoding
            return offset * u' ' + text
        else:
            return ''
    # fset
    def _setCssText(self, cssText):
        """
        sets inherited property cssText
        NOT IMPLEMENTED FULLY YET
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
            raise xml.dom.NoModificationAllowedErr('CharsetRule is readonly')
        raise exceptions.NotImplementedError()
    # property
    cssText = property(fget=getFormatted, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation.")
