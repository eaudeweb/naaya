"""
contains DOM Level 2 CSS ValueList implementation class.
DUMMY IMPLEMENTATION!

TODO
    pprint of value/unit e.g.   3 px  5px
                            ->  3px 5px
    simplify colors if possible e.g.
                                #ffaa55
                            ->  #fa5
    simplify values:    0px;
                    ->  0;
"""
__version__ = '0.51'

import xml.dom


class Value(object):
    """
    The CSSValue interface represents a simple or a complex value.
    A CSSValue object only occurs in a context of a CSS property
    """

    CSS_INHERIT = 0         # cssText contains "inherit".
    CSS_PRIMITIVE_VALUE = 1 # The value is a primitive value and an instance of the
                            # CSSPrimitiveValue interface can be obtained by using binding-specific
                            # casting methods on this instance of the CSSValue interface.
    CSS_VALUE_LIST = 2      # The value is a CSSValue list and an instance of the CSSValueList
                            # interface can be obtained by using binding-specific casting
                            # methods on this instance of the CSSValue interface.
    CSS_CUSTOM = 3          # The value is a custom value.
                            
    def __init__(self, text=None):
        """
        (cssutils)
        TODO
            DOMException:SYNTAX_ERR if value not parsable
        """
        if text:
            self._setCssText(text)
        else:
            self._text = None
            self._type = None

    # fget
    def _getFormatted(self):
        return self._text
    # fset
    def _setCssText(self, text):
        """
        Exceptions on setting
        DOMException
            SYNTAX_ERR: Raised if the specified CSS string value has a
                syntax error (according to the attached property) or is
                unparsable.
            INVALID_MODIFICATION_ERR: Raised if the specified CSS string
                value represents a different type of values than the values
                allowed by the CSS property.
            NO_MODIFICATION_ALLOWED_ERR: Raised if this value is readonly.
        """
        self._text = u' '.join(text.split())
        if self._text == u'inherit':
            self._type = self.CSS_INHERIT
        else:
            self._type = self.CSS_CUSTOM # TODO!
    # property         
    cssText = property(_getFormatted, _setCssText,
                    doc="A string representation of the current value.")

    # fget
    def _getValueType(self):
        return self._type
    # property
    cssValueType = property(_getValueType,
                            doc="A readonly code defining the type of the\
                            value as defined above.")    

    