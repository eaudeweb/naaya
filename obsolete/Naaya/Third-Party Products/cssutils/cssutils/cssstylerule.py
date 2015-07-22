"""
contains DOM Level 2 CSSStyleRule implementation class.

TODO
    cssText setting
    selectorText parsing and raising exceptions
    selector comments
    remove StyleRule init parameters
    
    auto box hacks?
    (normalize order of declarations -> CSSNormalizer)
    indent subrules if selector is subselector
        contains(selector)
        isSubselector(selector)
"""
__version__ = '0.51'

import cssrule
import xml.dom


class StyleRule(cssrule.CSSRule):
    """
    represents a single rule set in a CSS style sheet.
    """
    # CONSTANT
    type = cssrule.CSSRule.STYLE_RULE 

    def __init__(self, selector=None, style=None):
        self._selectors = []
        self._style = None
        if selector:
            self._setSelector(selector)
        if style:
            self._style = style
        
    def addSelector(self, selector):
        """
        (cssutils) add a selector (string) to this rule
        """
        for s in selector.split(u','):
            self._selectors.append(u' '.join(s.split()))

    def getSelectors(self):
        """
        (cssutils) returns a Python list of selector strings
        @see selectorText for a complete textual representation
        """
        return self._selectors
  
    # fget
    def getStyleDeclaration(self):
        """
        (cssutils) returns the StyleDeclaration object
        of this Rule
        use attribute cssText for a textual representation
        """
        return self._style
    # fset
    def setStyleDeclaration(self, style):
        """
        (cssutils) sets the style for this StyleRule to
        the given StyleDeclaration
        """
        self._style = style
    # property
    style = property(getStyleDeclaration, setStyleDeclaration,
                     doc="(DOM attribute) The declaration-block of this\
                     rule set. DOM attribute is readonly!")

    # fget
    def getFormatted(self, indent=4, offset=0):
        """
        (cssutils) pretty prints this rule
        """
        offsetspace = offset * u' '
        indentspace = indent * u' '
        out = []
        if self._style:
            out.append(offsetspace + self._getSelector() + u' {')
            out.append(self._style.getFormatted(indent, offset))
            out.append(offsetspace + indentspace + u'}')
        else:
            out.append(offsetspace + self._getSelector() + u' {}\n')
        return u'\n'.join(out)
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
            NO_MODIFICATION_ALLOWED_ERR: Raised if the rule is readonly.
        """
        import exceptions 
        raise exceptions.NotImplementedError()
    # property    
    cssText = property(getFormatted, _setCssText,
                       doc="(DOM attribute) The parsable textual\
                       representation of the rule.")

    # fget
    def _getSelector(self):
        return u', '.join(self._selectors)
    # fset
    def _setSelector(self, selector):
        if len(selector) == 0:
            raise xml.dom.SyntaxErr('Empty text for selectorText given.')
        self._selectors = [] # empty current
        self.addSelector(selector)
    # property
    selectorText = property(_getSelector, _setSelector, doc="\
            (DOM attribute) The textual representation of the selector for\
            the rule set.")

