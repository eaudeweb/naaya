"""
RuleList implements DOM Level 2 CSSRuleList.
"""

__version__ = '0.41'


class RuleList(list):
    """
    A list of rules contained in a stylesheet. Subclasses a
    standard Python list so you can use all standard list
    attributes.
    Implements DOM Level 2 CSSRuleList.
    """
    def _getLength(self):
        return len(self)

    length = property(_getLength, doc="(DOM attribute) The number of CSSRules in the list.")
    
    def item(self, index):
        """
        (DOM method) Used to retrieve a CSS rule by ordinal index.
        The order in this collection represents the order of the rules
        in the CSS style sheet. If index is greater than or equal to
        the number of rules in the list, this returns null (None).
        """
        try:
            return self[index]
        except IndexError:
            return None

