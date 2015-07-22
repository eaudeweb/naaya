# -*- coding: iso-8859-1

###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, unittest

from Products.TextIndexNG2.interfaces.ILexicon import LexiconInterface 
from Products.TextIndexNG2.classVerify import verifyClass
from Products.TextIndexNG2.lexicons.StandardLexicon import Lexicon

data = (
    'the quick brown fox jumps over the lazy dog',
    unicode('Bei den dreitägigen Angriffen seien auch bis'
            ' auf einen alle Flugplätze der Taliban zerstört worden',
            'latin1')
)

class StandardLexiconTests(unittest.TestCase):

    def setUp(self):
        self._lexicon = Lexicon(truncate_left=1)

    def cmp(self, x, y):
        if isinstance(x, list) and isinstance(y, list):
            self.assertEqual(x,y)
        else:
            i1 = x.items()
            i2 = y.items()
            self.assertEqual(i1,i2)

    def testInterface(self):
        verifyClass(LexiconInterface, self._lexicon.__class__)

    def testSimple(self):
        self.assertEqual(len(self._lexicon) ,0)
        self._lexicon.clear()
        self.assertEqual(len(self._lexicon) ,0)

    def testgetWordIdList(self):

        for s in data:
            self._lexicon.clear()
            
            wids1 = self._lexicon.getWordIdList(s.split())
            wids2 = self._lexicon.getWordIdList(s.split())
            
            self.cmp(wids1,wids2)

    def testgetWordIdLatin1(self):

        for s in data:            
            self._lexicon.clear()
            words = data[0].split()

            for w in words:

                wids = self._lexicon.getWordIdList([w]) # List or IIBucket
                self.assertEqual(len(wids),1)

                wid = self._lexicon.getWordId(w)  

                if isinstance(wids, list):
                    wids = wids[0]
                else:
                    wids = wids.keys()[0]

                self.assertEqual(wid, wids)

                w1 = self._lexicon.getWord(wids)
                self.assertEqual(w, w1)

    def testgetWordIdUnicode(self):

        for s in data:            
            self._lexicon.clear()
            words = data[1].split()

            for w in words:

                wids = self._lexicon.getWordIdList([w]) # List or IIBucket
                self.assertEqual(len(wids),1)

                wid = self._lexicon.getWordId(w)  # IISet
                self.assertEqual(len(wid),1)

                if isinstance(wids, list):
                    wids = wids[0]
                else:
                    wids = wids.keys()[0]

                self.assertEqual(wid.keys()[0], wids)

                w1 = self._lexicon.getWord(wids)
                self.assertEqual(w, w1)


    def testgetWordIdUnicode(self):

        for s in data:            
            self._lexicon.clear()
            words = data[1].split()

            for w in words:

                wids = self._lexicon.getWordIdList([w]) # List or IIBucket
                self.assertEqual(len(wids),1)

                wid = self._lexicon.getWordId(w)  # IISet

                if isinstance(wids, list):
                    wids = wids[0]
                else:
                    wids = wids.keys()[0]

                self.assertEqual(wid, wids)

                w1 = self._lexicon.getWord(wids)
                self.assertEqual(w, w1)


    def testRightTruncation(self):

        self._lexicon.clear()
        wids = self._lexicon.getWordIdList(data[0].split())

        RT = self._lexicon.getWordsForRightTruncation
        self.assertEqual(list(RT(u't')), ['the']   )     
        self.assertEqual(list(RT(u'th')), ['the']   )     
        self.assertEqual(list(RT(u'the')), ['the']   )     
        self.assertEqual(list(RT(u'thee')), []   )     
        self.assertEqual(list(RT(u'q')),  ['quick']   )     
        self.assertEqual(list(RT(u'f')), ['fox']   )     
        self.assertEqual(list(RT(u'fo')), ['fox']   )     

    def testLeftTruncation(self):

        self._lexicon.clear()
        wids = self._lexicon.getWordIdList(data[0].split())

        LT = self._lexicon.getWordsForLeftTruncation
        self.assertEqual(list(LT(u'the')), ['the']   )     
        self.assertEqual(list(LT(u'he')), ['the']   )     
        self.assertEqual(list(LT(u'e')), ['the']   )     
        self.assertEqual(list(LT(u'fox')), ['fox']   )     
        self.assertEqual(list(LT(u'ox')), ['fox']   )     
        self.assertEqual(list(LT(u'x')), ['fox']   )     


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(StandardLexiconTests))
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

