###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
Storage for wordIds/documentIds with forward and backward indexes 

$Id: StupidStorage.py,v 1.6 2005/03/28 14:05:47 ajung Exp $
"""

from Persistence import Persistent
import BTrees.Length 
from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IITreeSet, IISet 

from Products.TextIndexNG2.interfaces.IStorage import StorageInterface

class Storage(Persistent):
    """ A really stupid but memory efficient storage that does not
        support ranking.  
    """

    __implements__ = StorageInterface

    def __init__(self): 
        self.clear()

    def clear(self):
        self._forward_idx = IOBTree()   # WID -> [Docids]
        self._reverse_idx = IOBTree()   # DOCID -> [WIDs]
        self._length = BTrees.Length.Length()
    
    def __len__(self): return self._length()
    getNumDocuments = __len__
    
    def providesWordFrequencies(self): return False

    def getDocIds(self): return self._reverse_idx.keys()

    def insert(self, wids, docid):
        """ insert entries: 
            wids is either an integer or a sequence of integers.
            docid is an integer.
        """

        if isinstance(wids, int): wids = [wids]
        idx = self._forward_idx

        for wid in wids:
            try:
                idx[wid].insert(docid)
            except KeyError:
                idx[wid] = docid
            except:
                olddocid = idx[wid]
                idx[wid] = IITreeSet([olddocid, docid])

        # if not self._reverse_idx.has_key(docid): self._length.change(1)
        # DM 2004-08-18: it is obviously wrong to remember only the
        #  added wids and forget the wids already there
        #self._reverse_idx[docid] = IITreeSet(wids)
        if self._reverse_idx.has_key( docid):
            self._reverse_idx[docid].update(wids)
        else:
            self._length.change(1)
            self._reverse_idx[docid] = IITreeSet(wids)

    def getWordFrequency(self, docid, wid):
        return 1

    def removeWordIdsForDocId(self, docid, wids):

        for wid in wids:
            try:
                if isinstance(self._forward_idx[wid], int):
                    del self._forward_idx[wid]
                else:
                    self._forward_idx[wid].remove(docid)
                    if len(self._forward_idx[wid])==0:
                        del self._forward_idx[wid]
            except KeyError: pass

        old_wids = self._reverse_idx[docid].keys()
        new_wids = [w for w in old_wids if w not in wids]
        self._reverse_idx[docid] = IISet(new_wids)


    def removeDocument(self, docid):
        """ remove a document and all its words from the storage """
        
        try:
            wids = self._reverse_idx[docid]
        except KeyError: return

        del self._reverse_idx[docid]

        for wid in wids.keys():
            try:
                if isinstance(self._forward_idx[wid], int):
                    del self._forward_idx[wid]
                else: 
                    self._forward_idx[wid].remove(docid )
            except KeyError: pass
            
            try:
                if len(self._forward_idx[wid]) == 0:
                    del self._forward_idx[wid]
            except KeyError: pass

        self._length.change(-1)

    def getDocumentIdsForWordId(self, wid):
        """ return the sequence of document ids for a word id """
        if not wid: return ()
        r = self._forward_idx.get(wid)
        if not r: return ()
        if isinstance(r, int):
            return (r,)
        else:
            return self._forward_idx[wid].keys()

    get = getDocumentIdsForWordId

    def getWordIdsForDocId(self, docid):
        """ return a sequence of words contained in the document with 
            ID 'docId'
        """
        return self._reverse_idx[docid].keys()

