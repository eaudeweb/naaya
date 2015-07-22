"""
contains DOM Level 2 CSS ValueList implementation class.
"""
__version__ = '0.51'

import xml.dom


class ValueList(list):
    """
    The CSSValueList interface provides the abstraction of an ordered
    collection of CSS values.

    Some properties allow an empty list into their syntax. In that case,
    these properties take the none identifier. So, an empty list means
    that the property has the value none.
    """
    # fget
    def _getLength(self):
        return len(self)
    # property
    length = property(_getLength,
                doc="(DOM attribute) The number of CSSValues in the list.")

    def getFormatted(self):
        """
        (cssutils method) Returns a formatted string.
        TODO
            return 'none'
        """
        return u' '.join(self)

    def item(self, index):
        """
        (DOM method) Used to retrieve a CSSValue by ordinal index. The
        order in this collection represents the order of the values in the
        CSS style property. If index is greater than or equal to the number
        of values in the list, this returns null (None).
        """
        try:
            return self[index]
        except IndexError:
            return None

