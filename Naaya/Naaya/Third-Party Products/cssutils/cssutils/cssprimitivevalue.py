"""
contains DOM Level 2 CSS PrimitiveValue implemementation class.

TODO:
    conversion (mm->cm etc.)
    cssText: fset
    getXXXValue methods
    readonly
"""
__version__ = '0.51'

import exceptions
import xml.dom
import cssvalue


class PrimitiveValue(cssvalue.Value):
    """
    represents a single CSS Value.
    Might be obtained from the getPropertyCSSValue method
    of the CSSStyleDeclaration
    """
    
    CSS_UNKNOWN = 0 # only obtainable via cssText
    CSS_NUMBER = 1
    CSS_PERCENTAGE = 2
    CSS_EMS = 3
    CSS_EXS = 4
    CSS_PX = 5
    CSS_CM = 6
    CSS_MM = 7
    CSS_IN = 8
    CSS_PT = 9
    CSS_PC = 10
    CSS_DEG = 11
    CSS_RAD = 12
    CSS_GRAD = 13
    CSS_MS = 14
    CSS_S = 15
    CSS_HZ = 16
    CSS_KHZ = 17
    CSS_DIMENSION = 18
    CSS_STRING = 19
    CSS_URI = 20
    CSS_IDENT = 21
    CSS_ATTR = 22
    CSS_COUNTER = 23
    CSS_RECT = 24
    CSS_RGBCOLOR = 25

    _units = {
        0: u'__UNKNOWN',
        1: u'',
        2: u'%',
        3: u'em',
        4: u'ex',
        5: u'px',
        6: u'cm',
        7: u'mn',
        8: u'in',
        9: u'pt',
        10: u'pc',
        11: u'deg',
        12: u'rad',
        13: u'grad',
        14: u'ms',
        15: u's',
        16: u'hz',
        17: u'khz',
        18: u'__DIMENSION',
        19: u'__STRING',
        20: u'__URI',
        21: u'__IDENT',
        22: u'__ATTR',
        23: u'__COUNTER',
        24: u'__RECT',
        25: u'__RBG'
        }

    _floattypes = [CSS_NUMBER, CSS_PERCENTAGE, CSS_EMS, CSS_EXS,
                   CSS_PX, CSS_CM, CSS_MM, CSS_IN, CSS_PT, CSS_PC,
                   CSS_DEG, CSS_RAD, CSS_GRAD, CSS_MS, CSS_S,
                   CSS_HZ, CSS_KHZ, CSS_DIMENSION
                   ]
    _stringtypes = [CSS_ATTR, CSS_IDENT, CSS_STRING, CSS_URI]
    _countertypes = [CSS_COUNTER]
    _recttypes = [CSS_RECT]
    _rbgtypes = [CSS_RGBCOLOR]

    def __init__(self, readonly=False):
        """
        The type of the value as defined by the constants
        specified above.
        readonly
        self.value = ' '.join(value.split())
        """
        self._readonly = readonly
        self.primitiveType = self.CSS_UNKNOWN

    # fget
    def getFormatted(self):
        return self.value
    # fset
    def _setCssText(self, text):
        # DOMException:SYNTAX_ERR if value not parsable
        raise exceptions.NotImplementedError()
    # property
    cssText = property(getFormatted, _setCssText, "String Value")

    def getCounterValue(self):
        """
        (DOM method) This method is used to get the Counter value. If
        this CSS value doesn't contain a counter value, a DOMException
        is raised. Modification to the corresponding style property
        can be achieved using the Counter interface.
        """
        if self.primitiveType not in _countertypes:
            raise xml.dom.InvalidAccessErr(u'value is not a counter type')
        return self._value

    def getFloatValue(self, unitType):
        """
        (DOM method) This method is used to get a float value in a
        specified unit. If this CSS value doesn't contain a float value
        or can't be converted into the specified unit, a DOMException
        is raised.
        """
        if unitType not in self._floattypes:
            raise xml.dom.InvalidAccessErr(u'value is not a float type')
        return self._value
    
    def getRGBColorValue(self):
        """
        (DOM method) This method is used to get the RGB color. If this
        CSS value doesn't contain a RGB color value, a DOMException
        is raised. Modification to the corresponding style property
        can be achieved using the RGBColor interface.
        """
        if unitType not in self._rbgtypes:
            raise xml.dom.InvalidAccessErr(u'value is not a RGB value')
        return self._value
        
    def getRectValue(self):
        """
        (DOM method) This method is used to get the Rect value. If this CSS
        value doesn't contain a rect value, a DOMException is raised.
        Modification to the corresponding style property can be achieved
        using the Rect interface.
        """
        if unitType not in self._recttypes:
            raise xml.dom.InvalidAccessErr(u'value is not a Rect value')
        return self._value

    def getStringValue(self):
        """
        (DOM method) This method is used to get the string value. If the
        CSS value doesn't contain a string value, a DOMException is raised.

        Note: Some properties (like 'font-family' or 'voice-family')
        convert a whitespace separated list of idents to a string.
        """
        if unitType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(u'value is not a string type')
        return self._value
        
    def setFloatValue(self, unitType, floatValue):
        """
        (DOM method) A method to set the float value with a specified unit.
        If the property attached with this value can not accept the
        specified unit or the float value, the value will be unchanged and
        a DOMException will be raised.
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        if unitType not in self._floattypes:
            raise xml.dom.InvalidAccessErr(u'value is not a float type')
        self._value = floatValue
        self.primitiveType = 0 # TODO

    def setStringValue(self, stringType, stringValue):
        """
        (DOM method) A method to set the string value with the specified
        unit. If the property attached to this value can't accept the
        specified unit or the string value, the value will be unchanged and
        a DOMException will be raised.
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr()
        if unitType not in self._stringtypes:
            raise xml.dom.InvalidAccessErr(u'value is not a string type')
        self._value = floatValue
        self.primitiveType = 0 # TODO

  
