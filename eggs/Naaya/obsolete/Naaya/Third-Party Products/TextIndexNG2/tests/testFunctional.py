###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import os, sys, unittest

from Testing import ZopeTestCase
from Products.ZCatalog import ZCatalog 

ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG2')

class Tests(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.folder.manage_addProduct['ZCatalog'].manage_addZCatalog('catalog', 'catalog')
        self.catalog = getattr(self.folder, 'catalog')
        self.catalog.addIndex('SearchableText', 'TextIndexNG2')
        self.catalog.addIndex('PrincipiaSearchSource', 'TextIndexNG2')

    def _prepareTexts(self):
        """ import texts from 'texts' folder as DTML Document """

        from OFS.DTMLDocument import addDTMLDocument

        dirname = os.path.join(os.path.dirname(__file__), 'texts')
        files = os.listdir(dirname)
        self.num_files = 0
        for f in files:
            fname = os.path.join(dirname, f)
            if not os.path.isfile(fname): continue
            fp = open(fname) 
            addDTMLDocument(self.folder, id=f, title=f, file=fp)
            fp.close()
            self.num_files+=1

    def _indexTexts(self):
        """ index imported texts """
        for obj in [o for o in self.folder.objectValues('DTML Document') if o.getId().endswith('txt')]:
            self.catalog.catalog_object(obj, obj.absolute_url(1))
        
    def testSimple(self):
        self.assertEqual(len(self.catalog), 0)


    def testSearching(self):

        def extractIds(lst):
            r = [o.getObject().getId() for o in lst]
            r.sort()
            return r

        from OFS.DTMLDocument import addDTMLDocument
        from cStringIO import StringIO
        addDTMLDocument(self.folder, id='1.txt', file=StringIO('The quick brown fox jumps over the lazy dog'))
        addDTMLDocument(self.folder, id='2.txt', file=StringIO('dog lazy brown fox leap jumps over dog dog lazy quick'))
        self._indexTexts()
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'quick'})
        self.assertEqual(extractIds(result), ['1.txt', '2.txt'])
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'quick and leap'})
        self.assertEqual(extractIds(result), ['2.txt'])
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'quick or leap'})
        self.assertEqual(extractIds(result), ['1.txt', '2.txt'])
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : '"The quick brown fox jumps over the lazy lazy"'})
        self.assertEqual(extractIds(result), ['1.txt'])

    def testSimpleIndexing(self):
        self.assertEqual(len(self.catalog), 0)
        self._prepareTexts()
        self._indexTexts()
        self.assertEqual(len(self.catalog), self.num_files)           

    def testSimpleSearch(self):
        self.assertEqual(len(self.catalog), 0)
        self._prepareTexts()
        self._indexTexts()
        # DTML Documents have no 'SearchableText' method
        result = self.catalog.searchResults(SearchableText={'query' : 'Jesus'})
        self.assertEqual(len(result), 0) 
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'Jesus'})
        self.assertEqual(len(result), 0)
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'Mose'})
        self.assertEqual(len(result), 166)
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'Egon'})
        self.assertEqual(len(result), 0)
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'knecht mose'})
        self.assertEqual(len(result), 24)
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'knecht and mose'})
        self.assertEqual(len(result), 24)
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'knecht or mose'})
        self.assertEqual(len(result), 171)
        result = self.catalog.searchResults(PrincipiaSearchSource={'query' : 'gold and kalb'})
        self.assertEqual(len(result), 1)


def test_suite():
   return unittest.makeSuite(Tests)

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

