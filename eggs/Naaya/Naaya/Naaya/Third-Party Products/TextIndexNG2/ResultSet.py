#############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################

"""
ResultSet

$Id: ResultSet.py,v 1.25 2005/03/30 13:08:25 ajung Exp $
"""

from math import log, sqrt

from BTrees.IIBTree import IISet, IIBTree
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import intersection as IntIntersection, union as IntUnion, difference as IntDifference
from Products.ZCTextIndex.NBest import NBest

class ResultSet:
    """ class to keep results for TextIndexNG queries """

    def __init__(self, mapping, words): 
        """ 'mapping' is either an IOBTree containing the mapping  
            documentId to list of positions of a wid/word in this
            document or an IISet() with a list of documentIds.

            'words' is a list of words (from the query)
        """
        # create a new IOBTree with the documentIds as keys
        if isinstance(mapping, IISet):
            self._mapping = IOBTree()

            for k in mapping:
                self._mapping[k] = IISet() 
        else:
            self._mapping   = mapping

        self._result = IISet()
        self._docids = IISet(mapping.keys())
        self._words  = OOBTree(words)

        self.items   = self._mapping.items
        self.keys    = self._mapping.keys
        self.values  = self._mapping.values
        self.has_key = self._mapping.has_key


    def docIds(self):  return self._docids
    def mapping(self): return self._mapping
    def words(self):   return self._words  # fix this 
    def result(self):  return self._result # mapping docid -> score
    def __len__(self): return len(self._mapping)

    def __str__(self):
        return  'ResultSet([%s], %s)' % \
                (self.words(),str(self._mapping)) 
    __repr__ = __str__

    def cosine_ranking(self, index, hits=250):
        """ Calculate the ranking of the document based on the 
            cosine rule.
        """

        IDF = {}                # mapping term -> inverse document frequency
        cache = {}              # mapping term -> found docids
        wid_cache = {}          # mapping term -> wid
        N = len(index)          # length of collection
        nbest = NBest(hits)

        for term in self.words().keys():

            wid_cache[term] = wid = index.getLexicon().getWordId(term)                         
            docids = index.getStorage().getDocumentIdsForWordId(wid)
            cache[term] = docids

            # term frequence = number of documents a term appears in
            tf = len(docids)

            # calc and store the inverse document frequency given as
            # log(1+N/TF)
            if tf == 0: IDF[term] = 0
            else:       IDF[term] = log(1.0 + N / tf) 

        terms = list(self.words().keys())
        num_terms = len(terms)
        get_frequency = index.getStorage().getWordFrequency
        for docid in self.docIds():   # iterate over all found documents

            rank = 0.0                # ranking
            total_dwt = 0.0           # document weight

            for term in terms:
                if not docid in cache[term]: continue 

                # document term frequency = the number of times a term
                # appears within a particular document
                try:
                    dtf = get_frequency(docid, wid_cache[term])
                except KeyError:
                    continue

                # document term weight = the weight of a term within a
                # document and is calculated as:
                dtw = (1.0 + log(dtf)) * IDF[term] 

                # query term frequency and query max frequency are set
                # to 1 by default
                qtf = qmf = 1    

                # query term weight is the weight given to each term in the
                # query and is calculated as:        
                qtw = (0.5 + (0.5 * qtf/qmf)) * IDF[term] * self.words()[term]

                # add this stuff to the ranking
                rank += (qtw * dtw) 
                total_dwt += (dtw * dtw)
#                print 'q:%12d/%10s: dtf=%8.5f dtw=%8.5f rank=%8.5f totaldtw=%8.5f' % (docid, term.encode('iso-8859-15'),dtf, dtw,rank, total_dwt)

            total_dwt = sqrt(total_dwt)
            if total_dwt == 0:
                rank = 0
            else:
#                print "\t",rank, total_dwt, rank/total_dwt
#                rank = rank / total_dwt     # normalization
                rank = rank  / num_terms
                rank = int(rank * 1000 + 0.5)   # scale rank to be an integer

            nbest.add(docid, rank)

        self._result = IIBTree()
        for docid, score in nbest.getbest():
            self._result[docid] = score


#################################################################
# ResultSet functions
#################################################################

def intersectResultSets(sets):
    """ perform intersection of ResultSets """
                                    
    docids = None
    words = OOBTree()
    sets = list(sets)
    sets.sort(lambda s1,s2: cmp(len(s1.docIds()),len(s2.docIds())))

    for set in sets:
        docids = IntIntersection(docids, set.docIds())
        words.update(set.words())

    return ResultSet(docids, words)       

def unionResultSets(sets):
    """ perform union of ResultSets """

    docids = None
    words = OOBTree()
    sets = list(sets)
    sets.sort(lambda s1,s2: cmp(len(s1.docIds()),len(s2.docIds())))

    for set in sets:
        docids = IntUnion(docids, set.docIds())
        words.update(set.words())
    return ResultSet(docids,  words)       

def phraseResultSets(sets, index):
    """ quote is a special case of near search where the near-
        distance is one and we only search to the right
    """
    return nearResultSets(sets, index, distance=1, bidirectional=0)

def nearResultSets(sets, index, distance=5, bidirectional=1):
    """ perform near search on results sets """
    
    # One resultset consists of an IISet() or documentIds and 
    # tuple whose first element is the word (from LexiconLookup())
    # First we perform an intersection to get the documentIds of
    # those documents that contain all the words

    docids =  intersectResultSets(sets).docIds()

    # Now we determine for every document the positions of all
    # the words inside the document. Then we compare all the positions
    # to determine neighbourship
    
    words = []
    for set in sets:
        for word in set.words().keys():
            words.append(word)

    res_docids = IISet()

    for docId in docids:
        # the posMap is a list of tuples(word,IISet[positions])
        posMap = index.positionsFromDocumentLookup(docId, words)

        if bidirectional:
            if len(posMap.checkPositionMapBidirectional(distance)) > 0:
                res_docids.insert(docId)
        else:
            if len(posMap.checkPositionMapUnidirectional(distance)) > 0:
                res_docids.insert(docId)

    d = {}
    for w in words: d[w] = 1.0

    return ResultSet(res_docids, d)       

def inverseResultSet(set, index):
    """ compute inverse ResultSet (for NotNode) """

    docids = IntDifference(
                 IISet(index.getStorage().getDocIds()), 
                 set.docIds()
                )

    return ResultSet(docids,  set.words())       
