###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, unittest

from Products.TextIndexNG2.parsers.GermanQueryParser import Parser 
from Products.TextIndexNG2.interfaces.IParser import ParserInterface
from Products.TextIndexNG2.ParseTree import WordNode, TruncNode, GlobNode, SimNode
from Products.TextIndexNG2.ParseTree import AndNode, PhraseNode, NearNode, OrNode, NotNode
from Products.TextIndexNG2.classVerify import verifyClass

class TestBase(unittest.TestCase):


    def setUp(self):
        self.p = Parser()

    def testInterface(self):
        verifyClass(ParserInterface, Parser)

    
    def parse(self, q):
        return self.p.parse(q,'')

    def testSimple(self):

        self._test('a' ,   WordNode('a'))
        self._test('1' ,   WordNode('1'))
        self._test('foo' , WordNode('foo'))
        self._test('123' , WordNode('123'))

    def testWithSeparators(self):

        self._test('a' ,   WordNode('a'))
        self._test('1' ,   WordNode('1'))
        self._test('foo' , WordNode('foo'))
        self._test('C++' , WordNode('C++'))

    def testGlobbing(self):

        self._test('foo*',   TruncNode("foo"))
        self._test('%foo',   SimNode("foo"))
        self._test('fo?o*',  GlobNode("fo?o*"))
        self._test('?fo?o*', GlobNode("?fo?o*"))


    def testAnd(self):

        self._test('foo und bar', 
            AndNode((WordNode("foo"),WordNode("bar"))) )
        self._test('foo UND bar', 
            AndNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo und bar und sux', 
            AndNode(((WordNode("foo"),AndNode((WordNode("bar"),WordNode("sux")))))))
        self._test('C++ und Algol68' , 
            AndNode((WordNode('C++'),WordNode("Algol68"))))

        
    def testOR(self):
        self._test('foo oder bar', 
            OrNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo ODER bar', 
            OrNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo oder bar ODER sux', 
            OrNode((WordNode("foo"),OrNode((WordNode("bar"),WordNode("sux"))))))


    def testNear(self):

        self._test('foo nahe bar',   
            NearNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo NAHE bar', 
            NearNode((WordNode("foo"),WordNode("bar"))))


    def testPhrase(self):

        self._test('"foo"', 
            PhraseNode((WordNode("foo"),)))
        self._test('"foo bar"', 
            PhraseNode((WordNode("foo"),WordNode("bar"))))
        self._test('"foo bar sucks"' , 
            PhraseNode((WordNode("foo"),WordNode("bar"),WordNode("sucks"))))


    def testNot(self):

        self._test('NICHT  bar',
            NotNode(WordNode('bar')))
        self._test('nicht - bar',
            NotNode(NotNode(WordNode('bar'))))
        self._test('- bar',
            NotNode(WordNode('bar')))
        self._test('foo und nicht bar',
            AndNode((WordNode('foo'),NotNode(WordNode('bar')))))
        self._test('foo und -bar',
            AndNode((WordNode('foo'),NotNode(WordNode('bar')))))


    def testBastardQueries(self):
        
        self._test('andhausen oder oriole',
            OrNode((WordNode('andhausen'), WordNode('oriole'))))
        self._test('and oder or ',
            OrNode((WordNode('and'), WordNode('or'))))


class TestsNormal(TestBase):

    def _test(self, query, expected):

        got = self.parse(unicode(query, 'latin1'))
        self.assertEqual(got, expected, query)
 

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestsNormal))
    return s

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

