###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys,  unittest

from Products.TextIndexNG2.Stopwords import Stopwords
from Products.TextIndexNG2.interfaces.IStopwords import StopwordsInterface
from Products.TextIndexNG2.classVerify import verifyClass

class EightBitTests(unittest.TestCase):

    data = 'the quick brown fox jumps over the lazy dog and i am so proud'
    words = ('i','am','so','lazy')

    def setUp(self):
        self._sw = Stopwords('en', self.words)
        verifyClass(StopwordsInterface, self._sw.__class__)
        
    def testSimple(self):

        self.assertEqual( self._sw.getLanguage(), 'en')
        self.assertEqual( len(self._sw.getStopWords()), len(self.words) ) 

        for w in self.words:
            self.assertEqual(self._sw.isStopWord(w.lower()), 1)
            self.assertEqual(self._sw.isStopWord(w.upper()), 1)
            self.assertEqual(self._sw.isStopWord(w.capitalize()), 1)

    def testNonStopwords(self):

        self.assertEqual(self._sw.isStopWord('foo'), 0)
        self.assertEqual(self._sw.isStopWord('bar'), 0)

    def testFilter1(self):

        data = ''
        expected = [ w for w in data.split() if w not in self.words]
        self.assertEqual(self._sw.process(data.split()), expected)    

    def testFilter2(self):

        data = 'the quick brown fox jumps over the lazy dog and i am so proud'
        expected = [ w for w in data.split() if w not in self.words]
        self.assertEqual(self._sw.process(data.split()), expected)    
        

class UnicodeTests(EightBitTests):

    data = u'the quick brown fox jumps over the lazy dog and i am so proud'
    words = (u'i',u'am',u'so',u'lazy')


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(EightBitTests))
    s.addTest(unittest.makeSuite(UnicodeTests))
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

