"""
contains DOM Level 2 CSSMediaRule implementation class.

TODO
    insertRule: HIERARCHY_REQUEST_ERR
    cssText: fset
"""
__version__ = '0.51'

import xml.dom
import cssparser
import cssrule
import cssrulelist
import medialist
import cssstylerule


class MediaRule(cssrule.CSSRule):
    """
    represents a @media rule in a CSS style sheet.   
    """
    # CONSTANT
    type = cssrule.CSSRule.MEDIA_RULE 

    def __init__(self, media=u'', readonly=False):
        """(cssutils)
        @param media list of mediatypes as one string
        @param readonly 
        """
        self._media = medialist.MediaList()      
        if media != u'':
            for m in media.split(u','):
                self._media.appendMedium(m.strip())
        self._readonly = readonly
        self._nodes = []

    # fget
    def _getMedia(self):
        return self._media
    # property
    media = property(_getMedia,
                     doc=u"(DOM attribute) A list of media types for this\
                     rule of type MediaList")
    
    def addRule(self, rule):
        "(cssutils) append a new Rule to the media block."
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'MediaRule is readonly.')
        self._nodes.append(rule)

    def getRules(self, all=True):
        """
        (cssutils) returns a RuleList containing all rules in the media
        block.
        @param all if set to True also returns comments, else only Rules
        """
        if all:
            return cssrulelist.RuleList(self._nodes)
        else:
            return cssrule.RuleList(
                [n for n in self._nodes if not type(n) == cssutils.Comment]
                )

    # fget     
    def _getCssRules(self):
        "returns a RuleList containing only rules of the media block."
        return self.getRules(False)
    # property readonly?!
    cssRules = property(_getCssRules,
                        doc="A list of all CSS rules contained\
                        within the media block.")    

    def deleteRule(self, index):
        """
        (DOM attribute) Used to delete a rule from the media block.
        """        
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'MediaRule is readonly.')
        try:
            del self._nodes[index]
        except IndexError:
            raise xml.dom.IndexSizeErr(
                u'index %s not in the list with a len of %s' % (
                    index, len(self._nodes)))

    def insertRule(self, rule, index):
        """
        (DOM method) Used to insert a new rule into the media block.
        @rule
            The parsable text representing the rule. For rule sets this
            contains both the selector and the style declaration. For
            at-rules, this specifies both the at-identifier and the rule
            content.
        @index
            within the media block's rule collection of the rule before
            which to insert the specified rule. If the specified index is
            equal to the length of the media blocks's rule collection, the
            rule will be added to the end of the media block.
        @return
            The index within the media block's rule collection of the newly
            inserted rule.
        TODO
            HIERARCHY_REQUEST_ERR: Raised if the rule cannot be inserted at
            the specified index, e.g., if an @import rule is inserted after
            a standard rule set or other at-rule.
        """
        if self._readonly:
            raise xml.dom.NoModificationAllowedErr(
                u'MediaRule is readonly.')
        # not in w3c DOM
        if type(rule) == cssstylerule.StyleRule:
            r = rule.cssText
        # DOM parse
        else:
            p = cssparser.CSSParser(raiseExceptions=True)
            try:
                p.parseString(rule)
                r = p.getStyleSheet().getRules()[0]
            except xml.dom.SyntaxErr:
                raise
            except IndexError:
                raise xml.dom.SyntaxErr(u'"%s" contains no rule' % rule)
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

    # fget
    def getFormatted(self, indent=4):
        "(cssutils) pretty printed string representation"
        indentspace = indent * ' '
        out = []
        out.append(u'@media %s {' % (self.media.getFormatted()))
        for rule in self._nodes:
            out.append(rule.getFormatted(indent, indent))
        out.append(u'}')
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
        raise exceptions.NotImplementedError()
    # property
    cssText = property(getFormatted, _setCssText,
                       doc="parsable textual representation of the rule.")
