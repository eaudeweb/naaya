"""
classes to tokenize CSS StyleSheet strings
thanks to David Mertz for statemachine from his book
    "Text Processing in Python"

TODO
    comments everywhere
"""
__version__ = "0.51"

import statemachine


class StyleSheetLexer(object):
    """
    tokenizes a complete CSS StyleSheet string
    """    

    def __init__(self, log=None):
        """
        @param log parse messages, default is a file log.
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

    def _state_StyleSheet(self, cargo):
        """
        start state
        cargo is tuple (cssText remaining to deal with,
                        callerState to return to)
        """
        cssText, callerState = cargo
        t  = []
        while cssText:
            # CDO
            if u'<!--' == ''.join(cssText[:4]):
                del cssText[:4]
                continue
            # CDC
            elif u'-->' == ''.join(cssText[:3]):
                del cssText[:3]
                continue
            # TODO comment in selector !!!
            elif u'/*' == ''.join(cssText[:2]):
                if ''.join(t).strip(): self.log.info(u'\t(Lexer)Ignored\t"%s"' % ''.join(t))
                del cssText[:2]
                return self._state_Comment, (cssText, self._state_StyleSheet)
            # @ rule
            elif u'@' == cssText[0]:
                if ''.join(t).strip(): self.log.info(u'\t(Lexer)Ignored\t"%s"' % ''.join(t))
                return self._state_AtRule, (cssText, self._state_StyleSheet)
            # StyleRule
            elif u'{' == cssText[0]:
                cssText = t + cssText
                return self._state_StyleRule, (cssText, self._state_StyleSheet)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_Comment(self, cargo):
        cssText, callerState = cargo # TODO tunnel real callerState!
        t = []
        while cssText:
            if u'*/' == ''.join(cssText[:2]):
                self._tokens.append((u'Comment', ''.join(t).strip()))
                return callerState, (cssText[2:], None)
            elif u'/*' == ''.join(cssText[:2]):
                self.log.error(u'(Lexer)Forbidden nested comment: %s' % ''.join(t))
                del cssText[:2]
                continue
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_AtRule(self, cargo):
        cssText, callerState = cargo
        if u'@import ' == ''.join(cssText[:8]):
            del cssText[:8]
            return self._state_ImportRule, (cssText, callerState)
        elif u'@charset' == ''.join(cssText[:8]):
            del cssText[:8]
            return self._state_CharsetRule, (cssText, callerState)
        elif u'@font-face' == ''.join(cssText[:10]):
            del cssText[:10]
            return self._state_FontFaceRule, (cssText, callerState)
        elif u'@page' == ''.join(cssText[:5]):
            del cssText[:5]
            return self._state_PageRule, (cssText, callerState)
        elif u'@media ' == ''.join(cssText[:7]):
            del cssText[:7]
            return self._state_MediaList, (cssText, callerState)
        # UNKNOWN @, ignore upto ; or block {} if present
        else:
            inBlock = False
            t = []
            while cssText:
                if u';' == cssText[0] and not inBlock:
                    t.append(cssText[0])
                    del cssText[0]
                    self.log.info(u'(Lexer)Unknown at keyword, ignored\t"%s"' % ''.join(t))
                    return callerState, (cssText, None)
                elif u'}' == cssText[0]:
                    t.append(cssText[0])
                    del cssText[0]
                    if not inBlock:
                        self.log.error(u'(Lexer)End of block but no block started!')
                    self.log.info(u'(Lexer)Unknown at keyword, ignored\t"%s"' % ''.join(t))
                    return callerState, (cssText, None)
                elif u'{' == cssText[0]:
                    inBlock = True
                t.append(cssText[0])
                del cssText[0]                
            return self._state_ImportRule, (cssText, callerState)
            
    def _state_CharsetRule(self, cargo):
        "tunnels callerState"
        cssText, callerState = cargo
        t = []
        while cssText:
            if u';' == cssText[0]:
                v = ''.join(t).strip()
                v = v.replace(u'"', u'')
                v = v.replace(u"'", u'')
                self._tokens.append((u'@charset', v))
                del cssText[0]
                return callerState, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_ImportRule(self, cargo):
        "tunnels callerState"
        cssText, callerState = cargo
        t = []
        while cssText:
            if u';' == cssText[0]:
                self._tokens.append((u'@import', ''.join(t).strip()))
                del cssText[0]
                return callerState, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_FontFaceRule(self, cargo):
        "tunnels callerState"
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'{' == cssText[0]:
                self._tokens.append((u'@font-face', '@font-face'))
                del cssText[0]
                return self._state_StyleDeclaration, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_PageRule(self, cargo):
        "tunnels callerState"
        # TODO!!!
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'{' == cssText[0]:
                self._tokens.append((u'@page', ''.join(t).strip()))
                del cssText[0]
                return self._state_StyleDeclaration, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    # MediaRule
    def _state_MediaList(self, cargo):
        "tunnels callerState"
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'{' == cssText[0]:
                self._tokens.append((u'@media', ''.join(t).strip()))
                del cssText[0]
                return self._state_MediaRule, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_MediaRule(self, cargo):
        """
        tunnels callerState ??? overwritten by return of StyleRule
        TODO !
        """
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'{' == cssText[0]:
                cssText = t + cssText
                return self._state_StyleRule, (cssText, self._state_MediaRule)
            elif u'}' == cssText[0]:
                self._tokens.append((u'@media-END', '}'))
                if ''.join(t).strip(): self.log.error(u'((Lexer))Ignored\t"%s"' % ''.join(t))
                del cssText[0]
                return self._state_StyleSheet, (cssText, None) # next state can be other???
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    # StyleRule
    def _state_StyleRule(self, cargo):
        """
        parse a StyleRule starting with the selectors
        TODO comments, selectorparts
        """
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'{' == cssText[0]:
                self._tokens.append((u'StyleRule', ''.join(t).strip()))
                del cssText[0]
                return self._state_StyleDeclaration, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    def _state_StyleDeclaration(self, cargo):
        """ parse a StyleRule StyleDeclaration """
        return self._state_PropertyName, cargo

    def _state_PropertyName(self, cargo):
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'}' == cssText[0]:
                self._tokens.append((u'BLOCKEND', '}'))
                del cssText[0]
                return callerState, (cssText, None) # end stylerule TODO None???
            elif u':' == cssText[0]:
                self._tokens.append((u'Property', ''.join(t).strip()))
                del cssText[0]
                return self._state_PropertyValue, (cssText, callerState)
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, cargo)

    def _state_PropertyValue(self, cargo):
        cssText, callerState = cargo
        t = []
        while cssText:
            if u'}' == cssText[0]:
                self._tokens.append((u'Value', ''.join(t).strip()))
                self._tokens.append((u'BLOCKEND', '}'))
                del cssText[0]
                return callerState, (cssText, None) # end stylerule TODO None???
            elif u';' == cssText[0]:
                self._tokens.append((u'Value', ''.join(t).strip()))
                del cssText[0]
                return self._state_PropertyName, (cssText, callerState) # get next property
            t.append(cssText[0])
            del cssText[0]
        return self._state_EOF, (t, None)

    # end  
    def _state_EOF(self, cargo):
        cssText = cargo[0]
        if ''.join(cssText).strip():
            self.log.error(u'(EOF)NOT PROCESSED\t"%s"' % ''.join(cssText))
        return

    # HELPER
    def _normalizeWhitespace(self, cssText):
        # TODO no normalizing in comments!
        WHITESPACE = ' \t\r\n\f'
        for ws in WHITESPACE:
            cssText = cssText.replace(ws, ' ')
        cssText = ' '.join(cssText.split())
        return list(cssText)

    def lex(self, cssText):
        """
        lexes the cssText to (nodetype, nodevalue) tuples
        """
        # init StateMachine
        self.m = statemachine.StateMachine()
        self.m.add_state(self._state_StyleSheet)
        self.m.add_state(self._state_Comment)
        self.m.add_state(self._state_EOF, True)
        # @ rules
        self.m.add_state(self._state_AtRule)
        self.m.add_state(self._state_CharsetRule)
        self.m.add_state(self._state_FontFaceRule)
        self.m.add_state(self._state_ImportRule)
        self.m.add_state(self._state_PageRule)
        self.m.add_state(self._state_MediaList)
        self.m.add_state(self._state_MediaRule)
        # StyleRule
        self.m.add_state(self._state_StyleRule)
        self.m.add_state(self._state_StyleDeclaration)
        self.m.add_state(self._state_PropertyName)
        self.m.add_state(self._state_PropertyValue)
        self.m.set_start(self._state_StyleSheet)
        # run
        self._tokens = []
        cssText = self._normalizeWhitespace(cssText)
        self.m.run((cssText, None))
        return self._tokens
    