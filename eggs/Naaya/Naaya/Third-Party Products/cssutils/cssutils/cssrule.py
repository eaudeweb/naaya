"""
contains DOM Level 2 CSS CSSRule implementation class.

TODO
    abstract CSSRule attributes might need implementing
"""
__version__ = '0.51'

import exceptions
import xml.dom
import cssutils


class CSSRule(cssutils.Commentable):
    """
    abstract base interface for any type of CSS statement.
    This includes both rule sets and at-rules.
    """
    
    UNKNOWN_RULE = 0
    STYLE_RULE = 1
    CHARSET_RULE = 2
    IMPORT_RULE = 3
    MEDIA_RULE = 4
    FONT_FACE_RULE = 5
    PAGE_RULE = 6

    # The type of the rule, as defined above. The expectation is that
    # binding-specific casting methods can be used to cast down from an
    # instance of the CSSRule interface to the specific derived interface
    # implied by the type.
    #
    # overwritten in implementing classes as property
    # get=getFormatted, set=_setCssTextError()
    type = UNKNOWN_RULE

    # fget
    def getFormatted(self, indent='ignored', offset='ignored'):
        """
        The parsable textual representation of the rule. This reflects the
        current state of the rule and not its initial value.
        """
    # fset
    def _setCssText(self, cssText):
        """
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
    # property
    cssText = property(fget=getFormatted, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation\
            of the rule. MUST BE OVERWRITTEN IN SUBCLASS TO WORK!!!")

    # If this rule is contained inside another rule (e.g. a style rule
    # inside an @media block), this is the containing rule. If this rule
    # is not nested inside any other rules, this returns null.
    parentRule = property(doc="(DOM attribute) readonly attribute CSSRule\
        NOT IMPLEMENTED YET")

    # The style sheet that contains this rule.
    parentStyleSheet = property(
        doc="(DOM attribute) readonly attribute CSSStyleSheet\
        NOT IMPLEMENTED YET")


class UnknownRule(CSSRule):
    """
    represents an at-rule not supported by this user agent.
    NOT USED BY PARSER YET
    """    
    type = CSSRule.UNKNOWN_RULE

    def __init__(self):
        raise exceptions.NotImplementedError()

class SimpleAtRule:
    """
    DEPRECATED since v0.51
    use subclasses of CSSRule (CharsetRule, ImportRule, FontFaceRule
    or PageRule) instead
    """
    def __init__(self):
        raise exceptions.DeprecationWarning(
            u'Use subclasses of CSSRule instead.')


