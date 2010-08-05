"""
contains DOM Level 2 CSS ValueList implementation classes.
"""
__version__ = '0.51'

import exceptions
import xml.dom


class RGBColor(object):
    """
    The RGBColor interface is used to represent any RGB color value.
    This interface reflects the values in the underlying style property.
    Hence, modifications made to the CSSPrimitiveValue objects modify
    the style property.

    A specified RGB color is not clipped (even if the number is outside
    the range 0-255 or 0%-100%). A computed RGB color is clipped depending
    on the device.

    Even if a style sheet can only contain an integer for a color value,
    the internal storage of this integer is a float, and this can be used
    as a float in the specified or the computed style.

    A color percentage value can always be converted to a number and
    vice versa.
    
    // Introduced in DOM Level 2:
        interface RGBColor {
          readonly attribute CSSPrimitiveValue  red;
          readonly attribute CSSPrimitiveValue  green;
          readonly attribute CSSPrimitiveValue  blue;
        };
    """
    def __init__(self):
        raise exceptions.NotImplementedError()


class Rect(object):
    """
    The Rect interface is used to represent any rect value. This interface
    reflects the values in the underlying style property. Hence,
    modifications made to the CSSPrimitiveValue objects modify the style
    property.

    // Introduced in DOM Level 2:
        interface Rect {
          readonly attribute CSSPrimitiveValue  top;
          readonly attribute CSSPrimitiveValue  right;
          readonly attribute CSSPrimitiveValue  bottom;
          readonly attribute CSSPrimitiveValue  left;
        };    
    """
    def __init__(self):
        raise exceptions.NotImplementedError()


class Counter(object):
    """
    The Counter interface is used to represent any counter or counters
    function value. This interface reflects the values in the underlying
    style property.

    // Introduced in DOM Level 2:
        interface Counter {
          readonly attribute DOMString        identifier;
          readonly attribute DOMString        listStyle;
          readonly attribute DOMString        separator;
        };        
    """
    def __init__(self):
        raise exceptions.NotImplementedError()
    
    