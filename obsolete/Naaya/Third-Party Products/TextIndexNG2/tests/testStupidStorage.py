###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import sys, unittest 

from Products.TextIndexNG2.interfaces.IStorage import StorageInterface 
from Products.TextIndexNG2.Registry import StorageRegistry as SR
from Products.TextIndexNG2.classVerify import verifyClass
from Products.TextIndexNG2.storages.StupidStorage import Storage


class StorageTests(unittest.TestCase):

    def setUp(self):
        self._storage = Storage()

    def testInterface(self):
        verifyClass(StorageInterface, self._storage.__class__)

    def testSimple(self):
        self.assertEqual(len(self._storage), 0)
        self._storage.insert( (1,2,3,4,5), 1)
        self._storage.insert( (3,4,5,6,7), 2)
        self.assertEqual(len(self._storage), 2)
        self.assertEqual(list(self._storage.getDocIds()), list((1,2)))
        self._storage.removeDocument(9999)
        self._storage.removeDocument(2)
        self._storage.removeDocument(1)
        self.assertEqual(len(self._storage), 0)

    def testReindex(self):
        self.assertEqual(len(self._storage), 0)
        self._storage.insert( (1,2,3,4,5), 1)
        self._storage.insert( (3,4,5,6,7), 2)
        self._storage.insert( (3,4,22,32), 3)
        self.assertEqual(len(self._storage), 3)
        self.assertEqual(self._storage.getNumDocuments(), 3)
        self.assertEqual(list(self._storage.getDocIds()), list((1,2,3)))

        self._storage.insert( (20,21,23), 3)
        self.assertEqual(self._storage.getNumDocuments(), 3)
        self.assertEqual(list(self._storage.getDocIds()), list((1,2,3)))

        self.assertEqual(list(self._storage.getWordIdsForDocId(1)),
                         list( (1,2,3,4,5)))        
        self.assertEqual(list(self._storage.getWordIdsForDocId(2)),
                         list( (3,4,5,6,7)))        
        self.assertEqual(list(self._storage.getWordIdsForDocId(3)),
                         list( (3,4,20,21,22,23,32)))        

    def testReindexRemoving(self):
        self.assertEqual(len(self._storage), 0)
        self._storage.insert( (1,2,3,4,5), 1)
        self._storage.insert( (3,4,5,6,7), 2)
        self._storage.insert( (3,4,22,32), 3)

        self._storage.removeWordIdsForDocId(3, [22,32,100])
        self.assertEqual(list(self._storage.getWordIdsForDocId(3)),
                         list( (3,4)))        

    def testMultipleWids(self):
        self._storage.insert( (1,2,2,3,3,5), 1)
        self._storage.insert( (5,5,2,2,1), 2)

        self.assertEqual(list(self._storage.getWordIdsForDocId(1)),
                         list( (1,2,3,5)))        
        self.assertEqual(list(self._storage.getWordIdsForDocId(2)),
                         list( (1,2,5)))        
        self._storage.removeWordIdsForDocId(2, [5])
        self.assertEqual(list(self._storage.getWordIdsForDocId(2)),
                         list( (1,2)))        

    def testDocids(self):
        self._storage.insert( (1,2,3,4,5), 1)
        self._storage.insert( (3,4,5,6,7), 2)
        self._storage.insert( (3,4,22,32), 3)
        self.assertEqual( list(self._storage.getDocumentIdsForWordId(5)),
                          list( (1,2)))
        self.assertEqual( list(self._storage.getDocumentIdsForWordId(3)),
                          list( (1,2,3)))
        self.assertEqual( list(self._storage.getDocumentIdsForWordId(32)),
                          list( (3,)))
        self.assertEqual( list(self._storage.getDocumentIdsForWordId(987)),
                          [])

    def testWordFrequency1(self):
        self._storage.insert( (1,2,3,4,5,5,4,2,1,22), 1)
        self.assertEqual( (self._storage.getWordFrequency(1,1)), 1)
        self.assertEqual( (self._storage.getWordFrequency(1,2)), 1)
        self.assertEqual( (self._storage.getWordFrequency(1,3)), 1)
        self.assertEqual( (self._storage.getWordFrequency(1,4)), 1)
        self.assertEqual( (self._storage.getWordFrequency(1,5)), 1)
        self.assertEqual( (self._storage.getWordFrequency(1,22)), 1)

    def testWordFrequency2(self):
        self._storage.insert( (1,2,3,4,5,5,4,2,1,22), 1)
        self._storage.insert( (1,2,4,99,99), 2)
        self.assertEqual( (self._storage.getWordFrequency(2,1)), 1)
        self.assertEqual( (self._storage.getWordFrequency(2,2)), 1)
        self.assertEqual( (self._storage.getWordFrequency(2,4)), 1)
        self.assertEqual( (self._storage.getWordFrequency(2,99)), 1)
        self._storage.removeDocument(1)
        self._storage.removeDocument(3)
        self.assertEqual( (self._storage.getWordFrequency(2,1)), 1)
        self.assertEqual( (self._storage.getWordFrequency(2,2)), 1)
        self.assertEqual( (self._storage.getWordFrequency(2,4)), 1)
        self.assertEqual( (self._storage.getWordFrequency(2,99)), 1)

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(StorageTests))
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

