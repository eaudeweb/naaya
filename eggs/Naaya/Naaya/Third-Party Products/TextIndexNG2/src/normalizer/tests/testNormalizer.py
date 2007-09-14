###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, os, unittest
import normalizer

__basedir__ = os.getcwd()

class TestNormalizer(unittest.TestCase):


    def _doTest(self, text, table):

        N = normalizer.Normalizer( table )
        got = N.normalize(text)

        expected = text
        for old,new in table:
            expected = expected.replace(old, new)

        self.assertEqual(got, expected)

    def testSimple(self):
        
        N = normalizer.Normalizer( [] )
        self.assertEqual(N.getTable(), [] )

        N = normalizer.Normalizer( [('a','b'),('c','d'), ('a','b') ] )
        self.assertEqual(N.getTable(), [('a','b'),('c','d'), ('a','b') ]  )

    def test1(self):

        table = [ ('a','b'), ('c','d') ]
        text = 'the quick brown fox jumps over the lazy dog'
        self._doTest(text, table)

    def test2(self):

        table = [ ('a','bb'), ('bb','cc') ]
        text = 'the quick brown fox jumps over the lazy dog'
        self._doTest(text, table)
            
    def test3(self):

        table = [ ('foo','bar') ]
        text = 'the quick brown fox jumps over the lazy dog'
        self._doTest(text, table)

    def test4(self):

        table = [ ('ä','ae'), ('ö','oe') ]
        text = 'Bei den dreitägigen Angriffen seien auch bis'\
               'auf einen alle Flugplätze der Taliban zerstört worden'
        self._doTest(text, table)

    def test5(self):

        table = [ (u'Ä',u'Ae'), (u'Ö',u'Oe') ]
        text = unicode('Bei den dreitägigen Angriffen seien auch bis'\
               'auf einen alle Flugplätze der Taliban zerstört worden','latin1')
        self._doTest(text, table)


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestNormalizer))
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

