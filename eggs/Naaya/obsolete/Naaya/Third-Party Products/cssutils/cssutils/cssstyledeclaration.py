"""
contains DOM Level 2 CSSStyleDeclaration Implementation class

TODO:
    _setCssText
    return computed values and not literal values
    simplify unit pairs/triples/quadruples  2px 2px 2px 2px
                                    ->      2px for border/padding...
    normalize compound properties like:     background: no-repeat left url()  #fff
                                    ->      background: #fff url() no-repeat left     
"""

__version__ = '0.41'

import xml.dom 

import cssutils
import cssproperties


class StyleDeclaration(cssutils.Commentable):
    """
    The CSSStyleDeclaration class represents a single CSS declaration
    block. This class may be used to determine the style properties
    currently set in a block or to set style properties explicitly
    within the block.
    """

    def __init__(self, readonly=False):
        self._nodes = [] # properties and comments
        self._readonly = readonly

    def addProperty(self, name, value, priority=''):
        """
        DEPRECATED - use setProperty instead
        addProperty will be removed in a future version
        """
        self.setProperty(name, value, priority)

    def getProperties(self):
        """
        (cssutils) returns a list of all Property objects
        of this StyleDeclaration
        """
        return self._nodes

    def getProperty(self, name):
        """
        (cssutils) return the Property object of name
        """
        for p in self._nodes:
            if p.getName() == name:
                return p
        return None

    # fget
    def getFormatted(self, indent=4, offset=0):
        out = []
        for node in self._nodes:
            out.append(offset * u' ' + indent * u' ' + node.cssText)
        return u'\n'.join(out)
    # fset
    def _setCssText(self):
        """
        (DOM attribute) Setting this attribute will result in the parsing
        of the new value and resetting of all the properties in the
        declaration block including the removal or addition of properties.
        raises DOMException:SYNTAX_ERR or NO_MODIFICATION_ALLOWED_ERR
        if not parsable
        """
        raise exceptions.NotImplementedError
    # property
    cssText = property(getFormatted, _setCssText,
            doc="(DOM attribute) The parsable textual representation of\
            the declaration block excluding the surrounding curly braces.")

    def _length(self):
        return len(self._nodes)
    length = property(_length,
            doc="(DOM attribute) The number of properties that have been\
            explicitly set.")

    parentRule = property(doc="(DOM attribute) The CSS rule that contains\
            this declaration block or null if this CSSStyleDeclaration is\
            not attached to a CSSRule. NOT IMPLEMENTED YET")

    def getPropertyCSSValue(self, name):
        """
        (DOM method) Used to retrieve the object representation of
        the value of a CSS property if it has been explicitly set
        within this declaration block. This method returns null if
        the property is a shorthand property. Shorthand property
        values can only be accessed and modified as strings, using
        the getPropertyValue and setProperty methods.

        TODO
            shorthand properties
        """
        p = self.getProperty(name)
        if p:
            return p.getCSSValue()
        else:
            return None

    def getPropertyPriority(self, name):
        """
        (DOM method) Used to retrieve the priority of a CSS property
        (e.g. the "important" qualifier) if the property has been
        explicitly set in this declaration block.
        """
        p = self.getProperty(name)
        if p:
            return p.getPriority()
        else:
            return u''

    def getPropertyValue(self, name):
        """
        (DOM method) Used to retrieve the value of a CSS property
        if it has been explicitly set within this declaration block.
        """
        p = self.getProperty(name)
        if p:
            return p.getValue()
        else:
            return u''

    def item(self, index):
        """
        (DOM method) Used to retrieve the properties that have been
        explicitly set in this declaration block. 
        @returns the Declaration at the given position
        TODO:
            what with comment nodes?
        """            
        try:
            return self._nodes[index].getName()
        except IndexError:
            return u''
    
    def removeProperty(self, name):
        """
        (DOM method) Used to remove a CSS property if it has been
        explicitly set within this declaration block.
        @return the value of the removed property
        TODO
            property readonly, raise NoModificationAllowedErr
        """
        if (self._readonly):
            raise xml.dom.NoModificationAllowedErr(
                'StyleDeclaration is readonly')
        try:
            r = self.getPropertyValue(name)
            self._nodes.remove(self.getProperty(name))
        except ValueError:
            pass
        return r

    def setProperty(self, name, value, priority=''):
        """
        (DOM method) Used to set a property value and priority
        within this declaration block.
        """
        self.removeProperty(name) # might raise if property readonly
        try:
            self._nodes.append(
                cssproperties.Property(name, value, priority))
        except xml.dom.SyntaxErr:
            raise
