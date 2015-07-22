__version__ = '0.5d'

import unittest

import logging
import pprint 
import StringIO

import cssutils.lexer 


class CSSLexerTestCase(unittest.TestCase):

    def setUp(self):
        # clear old log
        self.logfile = 'lexertest.log'
        open(self.logfile, 'w').truncate(0)
        # logger for lexer
        log = logging.getLogger('lexertest')
        hdlr = logging.FileHandler(self.logfile)      
        formatter = logging.Formatter('%(levelname)s\t%(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
        log.setLevel(logging.DEBUG)
        # init lexer
        self.lex = cssutils.lexer.StyleSheetLexer(log)

    def test_basecss(self):
        cssText = """
            <!--
            /* comment */
            -->
            <!--
            a { color: red;}
            -->
            """
        expectedtokens = [
            (u'Comment', 'comment'),
            (u'StyleRule', 'a'),
            (u'Property', 'color'),
            (u'Value', 'red'),
            (u'BLOCKEND', '}')]
        actualtokens = self.lex.lex(cssText)
        log = open(self.logfile).read()
        #pprint.pprint(actualtokens)
        #print "\nlexer log:\n", log
        self.assertEqual(expectedtokens, actualtokens)
        self.assertEqual('', log)

    def test_media(self):
        cssText = """
            @media all, print {
            /* comment */
            a { color: red;}
            }
            """
        expectedtokens = [(u'@media', 'all, print'),
            (u'StyleRule', '/* comment */ a'),
            (u'Property', 'color'),
            (u'Value', 'red'),
            (u'BLOCKEND', '}'),
            (u'@media-END', '}')]
        actualtokens = self.lex.lex(cssText)
        log = open(self.logfile).read()
        #pprint.pprint(actualtokens)
        #print "\nlexer log:\n", log
        self.assertEqual(expectedtokens, actualtokens)
        self.assertEqual('', log)

        actualtokens = self.lex.lex(cssText)
        log = open(self.logfile).read()
        #pprint.pprint(actualtokens)
        #print "\nlexer log:\n", log
        self.assertEqual(expectedtokens, actualtokens)
        self.assertEqual('', log)


if __name__ == '__main__':
    unittest.main() 
