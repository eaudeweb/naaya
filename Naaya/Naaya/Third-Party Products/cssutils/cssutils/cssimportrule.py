"""
contains DOM Level 2 CSSImportRule implementation class.

TODO
    stylesheet: read and parse linked stylesheet
"""
__version__ = '0.51'

import exceptions 
import xml.dom

import cssrule
import medialist


class ImportRule(cssrule.CSSRule):
    """
    represents a @import rule within a CSS style sheet.
    """
    type = cssrule.CSSRule.IMPORT_RULE # CONSTANT

    def __init__(self, media=u'', href=u'', readonly=False):
        """
        media of type stylesheets::MediaList, readonly
            A list of media types for which this style sheet may be used.
        styleSheet of type CSSStyleSheet, readonly
            The style sheet referred to by this rule, if it has been
            loaded. The value of this attribute is null if the style sheet
            has not yet been loaded or if it will not be loaded (e.g. if
            the style sheet is for a media type not supported by the user
            agent).
        """
        # A list of media types for this rule. DOM readonly!
        self._media = medialist.MediaList()    
        if media != u'':
            for m in media.split(u','):
                self._media.appendMedium(m.strip())
        self._href = href
        self._readonly = readonly
        # self._styleSheet = None
    
    # fget
    def _getHref(self):
        return (self._href)
    # property
    href = property(_getHref,
        doc="(DOM)The location of the style sheet to be imported.\
        The attribute will not contain the url(...) specifier\
        around the URI.")

   # fget
    def _getMedia(self):
        return self._media
    # property
    media = property(_getMedia,
                     doc=u"(DOM attribute) A list of media types for this\
                     rule of type MediaList")
    
    # fget
    def getFormatted(self, indent=0, offset=0):
        "returns inherited property cssText or the empty string"
        if self._href:
            text = u'@import %s url(%s);' % (
                self.media.mediaText, self._href)
            return offset * u' ' + text
        else:
            return ''
    # fset
    def _setCssText(self, cssText):
        """
        sets inherited property cssText
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
        """
        if (self._readonly):
            raise xml.dom.NoModificationAllowedErr(
                'ImportRule is readonly')
        raise exceptions.NotImplementedError()
    # property
    cssText = property(fget=getFormatted, fset=_setCssText,
        doc="(DOM attribute) The parsable textual representation.")
