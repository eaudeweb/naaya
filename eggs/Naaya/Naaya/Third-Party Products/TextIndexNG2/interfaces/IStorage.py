###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class StorageInterface(Interface.Base):
    """ interface for storages to keep the mapping wordId to sequence
        of document ids and vis-versa.
    """
    
    def getDocIds(): 
        """ return a sequence with all document Ids """

    def getNumDocuments(): 
        """ return number of documents """

    def insert(wordIds, docId):
        """ insert entries: 
            wordIds is either an integer or a sequence of integers.
            docId is an integer.
        """

    def removeDocument(docId):
        """ remove a document and all its words from the storage """

    def getDocumentIdsForWordId(wordId):
        """ return the sequence of document ids for a word id """

    def getWordIdsForDocId(docId):
        """ return a sequence of words contained in the document with 
            ID 'docId'
        """
    def getWordFrequency(docId, wid):
        """ return the # occurences of a wid with a document """   

    def providesWordFrequencies():
        """" returns True|False if it support storing word frequencies """
