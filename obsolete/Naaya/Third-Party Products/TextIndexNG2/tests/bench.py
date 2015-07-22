###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import os, sys, unittest, time
import hotshot, hotshot.stats

from Testing import ZopeTestCase
from Products.ZCatalog import ZCatalog 

ZopeTestCase.installProduct('ZCatalog')
ZopeTestCase.installProduct('TextIndexNG2')

class Args:

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def keys(self):
        return self.__dict__.keys()


class Tests(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.folder.manage_addProduct['ZCatalog'].manage_addZCatalog('catalog', 'catalog')
        self.catalog = getattr(self.folder, 'catalog')
        args = Args(use_storage='StupidStorage')
        self.catalog.manage_addIndex('PrincipiaSearchSource', 'TextIndexNG2', extra=args)

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

    def _indexTexts(self, objs):
        """ index imported texts """
        for obj in objs:
            self.catalog.catalog_object(obj, obj.absolute_url(1))
        
    def testBench(self):
        self._prepareTexts()
        objs = [o for o in self.folder.objectValues('DTML Document') if o.getId().endswith('txt')]
        print len(objs), 'objects to be indexed'
        prof = hotshot.Profile('textindexng.prof')
        ts = time.time()
        prof.runcall(self._indexTexts, objs)
        te = time.time()
        print 'Indexing terminated (Duration: %5.3f seconds, %5.5f seconds/document)' % ((te-ts), (te-ts)/len(objs))
        stats = hotshot.stats.load('textindexng.prof')
        stats.strip_dirs()
        stats.sort_stats('cumulative')
#        stats.sort_stats('time', 'calls')
        stats.print_stats(25)


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

