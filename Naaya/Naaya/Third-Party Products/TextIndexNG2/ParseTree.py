###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
ParseTree

$Id: ParseTree.py,v 1.23 2004/10/30 06:39:06 ajung Exp $
"""

from Products.TextIndexNG2.interfaces.IParseTreeNode import IParseTreeNode
from ResultSet import unionResultSets, intersectResultSets
from ResultSet import nearResultSets, phraseResultSets, inverseResultSet
import TXNGSplitter


class BaseNode:
    """ base class for all nodes """

    __implements__ = IParseTreeNode

    def __init__(self, v):
        if isinstance(self.__class__, BaseNode):
            raise ImplementationError, "don't instantiate BaseNode"
        self._value = v

    def getType(self): return self.__class__.__name__
    def getValue(self): return self._value

    def __cmp__(self, node):
        if self.getType()==node.getType() and \
           self.getValue()==node.getValue(): 
            return 0
        else: return -1 
           
    def __repr__(self):
        return "%s(%r)" % (self.getType(), self.getValue())


class WordNode(BaseNode):
    """ normal word """

class GlobNode(BaseNode):
    """ globbing """

class TruncNode(BaseNode):
    """ right truncation """

class SubstringNode(BaseNode):
    """ substring """

class LTruncNode(BaseNode):
    """ left truncation """

class SimNode(BaseNode):
    """ similarity """

class NotNode(BaseNode):
    """ NOT node """

class AndNode(BaseNode):
    """ AND node """

class OrNode(BaseNode):
    """ OR node """
    
class NearNode(BaseNode):
    """ NEAR node """

class PhraseNode(BaseNode):
    """ Phrase node """ 

class RangeNode(BaseNode):
    """ Range node """ 


class Evaluator:
    """ evaluator for a ParseTree instance """

    def __init__(self, index):
        self._index = index
        self._splitter = TXNGSplitter.TXNGSplitter(casefolding=0,separator=index.splitter_separators)

    def normalize_word(self, word):
        """ normalize a word according to the splitter seperators """

        # There seems to be a bug in the splitter where single characters
        # are returned as empty string

        res = self._splitter.split(word)
        if res:
            return self._splitter.split(word)[0]
        else:
            return word

    def __call__(self, node):

        if isinstance(node, WordNode):
            word =  node.getValue() 
            return self._index.lookupWord( self.normalize_word(word))

        elif isinstance(node, AndNode):
            sets = [ self(n) for n in node.getValue() ]
            return intersectResultSets(sets) 

        elif isinstance(node, OrNode):
            sets = [ self(n) for n in node.getValue() ]
            return unionResultSets(sets) 

        elif isinstance(node, GlobNode):
            return self._index.lookupWordsByPattern( node.getValue() )

        elif isinstance(node, TruncNode):
            return self._index.lookupWordsByTruncation(node.getValue(), right=1)

        elif isinstance(node, LTruncNode):
            return self._index.lookupWordsByTruncation(node.getValue(), left=1)

        elif isinstance(node, SubstringNode):
            return self._index.lookupWordsBySubstring(node.getValue())

        elif isinstance(node, RangeNode):
            return self._index.lookupRange(node.getValue()[0], node.getValue()[1])

        elif isinstance(node, SimNode):
            return self._index.lookupWordsBySimilarity( node.getValue() )

        elif isinstance(node, NotNode):
            rset = self(node.getValue())
            return inverseResultSet(rset, self._index)

        elif isinstance(node, NearNode):
            sets = [ self(n) for n in node.getValue() ]
            return nearResultSets(sets, self._index, distance=self.near_distance) 

        elif isinstance(node, PhraseNode):
            sets = [ self(n) for n in node.getValue() if n]
            return phraseResultSets(sets, self._index) 
            
        else:
            raise ValueError, node
                                
