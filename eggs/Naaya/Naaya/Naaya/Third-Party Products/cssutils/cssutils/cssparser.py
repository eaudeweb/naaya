"""
contains a CSSParser implementation

Usage
    p = CSSParser(raiseExceptions=False)
    filename = 'J:/dev/cssutils/test/test1.css'
    css = p.parse(filename)
    css.pprint()
"""
__version__ = "0.51"

import xml.dom

import lexer
import cssbuilder


class CSSParser(object):
    """
    parses a CSS StyleSheet string or file and
    returns a DOM Level 2 CSS StyleSheet object
    """
    def __init__(self, log=None, raiseExceptions=False):
        """
        @param log to log parse messages, default is a file log.
        @param raiseExceptions
            True: Errors will be reported to the calling app,
                e.g. during building
            False: Errors will be written to the log, this is the
                default behaviour when parsing
        """
        if not log:
            import logging
            import time
            self.log = logging.getLogger('parser')
            t = time.strftime('%y%m%d') #time.strftime('%y%m%d_%H%M%S')
            hdlr = logging.FileHandler('parser_%s.log' % t)      
            formatter = logging.Formatter('%(levelname)s\t%(message)s')
            hdlr.setFormatter(formatter)
            self.log.addHandler(hdlr)
            self.log.setLevel(logging.DEBUG)
        else:
            self.log = log
        self.raiseExceptions = raiseExceptions

    def _buildImportRule(self, text):
        "parse @import string, e.g.: tv, print url(test.css)"
        try:
            media, href = text.split(u' url(')
            href = href[:-1].strip()
            return cssbuilder.ImportRule(media, href)
        except ValueError:
            msg = u'(Parser)IGNORED @import %s - not valid' % text
            if self.raiseExceptions:
                raise xml.dom.SyntaxErr(msg)
            else:
                self.log.error(msg)
        else:
            return None

    def _buildFontFaceRule(self, tokens):
        d = self._buildStyleDeclaration(tokens)
        if d:
            return cssbuilder.FontFaceRule(d)
        else:
            return None
        
    def _buildPageRule(self, selectorText, tokens):
        d = self._buildStyleDeclaration(tokens)
        if d:
            return cssbuilder.PageRule(selectorText, d)
        else:
            return None

    def _buildStyleRule(self, selectorText, tokens):
        r = cssbuilder.StyleRule()
        try:
            r.selectorText = selectorText
        except xml.dom.SyntaxErr, e:
            if self.raiseExceptions:
                raise
            else:
                self.log.error(u'(Parser)%s' % e)
        d = self._buildStyleDeclaration(tokens)
        if d:
            r.setStyleDeclaration(d)
            return r
        else:
            return None

    def _buildStyleDeclaration(self, tokens):
        d = cssbuilder.StyleDeclaration()
        while tokens:
            pt, pv = tokens[0]
            if pt == u'BLOCKEND':
                break
            elif pt == u'Property':
                vt, vv = tokens[1]
                if vt != u'Value':
                    msg = u'(Parser)Property with no Value!'
                    if self.raiseExceptions:
                        raise xml.dom.SyntaxErr(msg)
                    else:
                        self.log.error(msg)
                        continue
                if vv.endswith(u'!important'):
                    vv = vv[:-10]
                    priority = u'important'
                else:
                    priority = u''
                try:
                    d.addProperty(pv, vv, priority)
                except xml.dom.SyntaxErr, e:
                    if self.raiseExceptions:
                        raise
                    else:
                        self.log.error(u'(Parser)%s' % e)
                del tokens[:2]
            else:
                # comment?
                del tokens[0]
        # check if normal end of block
        if pt == u'BLOCKEND':
            del tokens[0]
        else:
            msg = u'Block not ended normally with }'
            if self.raiseExceptions:
                raise xml.dom.SyntaxErr(msg)
            else:
                self.log.error(msg)
        if d.length > 0:
            return d
        else:
            return None

    def _build(self, tokens):
        """
        builds the StyleSheet
        """
        css = cssbuilder.StyleSheet()
        current = css
        while tokens:
            t, v = tokens[0]
            if u'Comment' == t:
                current.addComment(cssbuilder.Comment(v))
            elif u'@charset' == t:
                r = cssbuilder.CharsetRule(v)
                current.addRule(r)
            elif u'@font-face' == t:
                r = self._buildFontFaceRule(tokens)
                if r:
                    current.addRule(r)
                continue
            elif u'@import' == t:
                r = self._buildImportRule(v)
                if r:
                    try:
                        current.addRule(r)
                    except xml.dom.HierarchyRequestErr, e:
                        if self.raiseExceptions:
                            raise 
                        else:
                            self.log.error(u'(Parser)IGNORED, %s)' % e)
            elif u'@page' == t:
                r = self._buildPageRule(v, tokens)
                if r:
                    current.addRule(r)
                continue
            elif u'@media' == t:
                css = current
                current = cssbuilder.MediaRule(v)
            elif u'@media-END' == t:
                css.addRule(current)
                current = css
            elif u'StyleRule' == t:
                r = self._buildStyleRule(v, tokens)
                if r:
                    current.addRule(r)
                continue
            else:
                # log here always!
                self.log.error(u'(Parser)Unrecognized Token "%s" with value "%s"' % (t, v))
            if tokens:
                del tokens[0]
        css = current
        return css
                
    def parseString(self, cssText):
        """
        parse a CSS StyleSheet string
        returns the parsed CSS as a StyleSheet object
        """
        lex = lexer.StyleSheetLexer(self.log)
        tokens = lex.lex(cssText)
        # DEBUG
        #import pprint
        #pprint.pprint(tokens)
        #print

        self.css = self._build(tokens)
        return self.css

    def parse(self, filename):  
        """
        parse a CSS StyleSheet file
        returns the parsed CSS as a StyleSheet object
        """
        return self.parseString(open(filename).read())

    def getStyleSheet(self):
        "returns the parsed CSS as a StyleSheet object"
        return self.css


if __name__ == '__main__':
    import sys
    try:
        filename = sys.argv[1]
    except:
        print 'usage:_ python cssutils.cssparser cssfilename'
        sys.exit(0)
    if 'debug' == filename:
        p = CSSParser(raiseExceptions=False)
        filename = 'J:/dev/cssutils/test/test1.css'
        css = p.parse(filename)
        css.pprint()
    else:
        p = CSSParser(raiseExceptions=False)
        css = p.parse(filename)
        css.pprint()


