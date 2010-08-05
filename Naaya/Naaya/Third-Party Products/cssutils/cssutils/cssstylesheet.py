"""
contains DOM Level 2 CSS CSSStyleSheet implementation class.

TODO
    ownerRule
    proper readonly
CHECK
    insertRule HIERARCHY_REQUEST_ERR for all cases?
"""
__version__ = '0.51'

import types
import xml.dom

import cssutils
import cssparser
import cssrule
import cssrulelist
import cssstylerule


class StyleSheet(cssutils.Commentable):
    """
    used to represent a CSS style sheet i.e., a style sheet
    whose content type is "text/css".
    """
    def __init__(self, readonly=False):
        self._readonly = readonly
        self._nodes = []

    def addRule(self, rule):
        """
        (cssutils method) append a Rule to the StyleSheet.
        @param rule the Rule object or string
        @see insertRule()
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'StyleSheet is readonly.')
        self.insertRule(rule, len(self._nodes))
            
    def getRules(self, all=True):
        """
        (cssutils method) get a list of all rules in the StyleSheet.
        by default includes all comment rules
        @param all set to 0 returns only CSS rules, no comments
        @return the rules as a Python list
        @see cssRules
        """
        if all:
            return cssrulelist.RuleList(self._nodes)
        else:
            return cssrulelist.RuleList(
                [n for n in self._nodes if not type(n) == cssutils.Comment]
                )

    def pprint(self, indent=4):
        """
        (cssutils method) pretty prints the complete StyleSheet.
        @param indent number of spaces
        """
        print self._pprint(indent)

    def _pprint(self, indent=4):
        """
        (cssutils method) returns a pretty printed string representation.
        """
        out = []
        for node in self._nodes:
            # WHY???
            if node.cssText:
                out.append(node.getFormatted(indent))
        return '\n'.join(out)

    # fget    
    def _getCssRules(self):
        "get only Style and At Rules, not the comments"
        return self.getRules(False)
    # property
    cssRules = property(_getCssRules,
                        doc="(DOM attribute) The list of all CSS\
                        rules contained within the style sheet.")

    # TODO
    # If this style sheet comes from an @import rule, the ownerRule
    # attribute will contain the CSSImportRule. In that case, the ownerNode
    # attribute in the StyleSheet interface will be null. If the style
    # sheet comes from an element or a processing instruction, the
    # ownerRule attribute will be null and the ownerNode attribute will
    # contain the Node.
    # fget fset
    def _getsetOwnerRuleDummy(self):
        "NOT IMPLEMENTED YET"
        raise exceptions.NotImplementedError()
    # property
    ownerRule = property(_getsetOwnerRuleDummy, _getsetOwnerRuleDummy,
                         doc="(DOM attribute) NOT IMPLEMENTED YET")

    def deleteRule(self, index):
        """
        (DOM method) Used to delete a rule from the style sheet.
        @param index of the rule to remove in the StyleSheet's rule list  
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'StyleSheet is readonly.')
        try:
            del self._nodes[index]
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'index %s not in the list with len %s' % (
                    index, len(self._nodes)))

    def insertRule(self, rule, index):
        """
        (DOM method) Used to insert a new Rule *string* into the
        style sheet. The new rule now becomes part of the cascade.
        (cssutils) rule may also be a Rule object
        @param rule as parsable DOMString (or Rule object)
        @param index: The index within the style sheet's rule list
            of the rule before which to insert the specified rule.
            If the specified index is equal to the length of the
            style sheet's rule collection, the rule will be added
            to the end of the style sheet.
        @return: The index within the style sheet's rule collection
            of the newly inserted rule.          
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'StyleSheet is readonly.')
        # parse
        if type(rule) in types.StringTypes:
            p = cssparser.CSSParser(raiseExceptions=True)
            try:
                p.parseString(rule)
                rule = p.getStyleSheet().getRules()[0]
            except xml.dom.SyntaxErr:
                raise
            except IndexError:
                raise xml.dom.SyntaxErr(u'"%s" contains no rule' % rule)
        # check @import
        if cssrule.CSSRule.IMPORT_RULE == rule.type:
            for n in self._nodes[:index]:
                # comments have to type!
                if n.type and n.type != cssrule.CSSRule.IMPORT_RULE:
                    raise xml.dom.HierarchyRequestErr(
                        '@import-rule must be before other rules')
        # insert
        if index < 0:
            index = 0
        if index > len(self._nodes):
            raise xml.dom.IndexSizeErr(
                u'%s bigger than current list, len only %s.' % (
                    index, len(self._nodes)))
        else:
            self._nodes.insert(index, rule)
            return index

    