###########################################################################
#
# LICENSE.txt for the terms of this license.
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
TextIndexNG 
Written by Andreas Jung

E-Mail: andreas@andreas-jung.com

$Id: TextIndexNG.py,v 1.167 2005/05/19 10:22:35 ajung Exp $
"""

import sys

from Globals import DTMLFile, InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from zLOG import ERROR, WARNING, LOG
from OFS.SimpleItem import SimpleItem
from Products.PluginIndexes import PluggableIndex       
from Products.PluginIndexes.common.util import parseIndexRequest
from OFS.content_types import guess_content_type
from BTrees.IIBTree import IISet, difference 
from classVerify import verifyClass

from Products.TextIndexNG2.ResultSet import ResultSet
from Products.TextIndexNG2.Registry import ParserRegistry, ConverterRegistry, NormalizerRegistry, StorageRegistry, ThesaurusRegistry
from Products.TextIndexNG2.Registry import LexiconRegistry, SplitterRegistry, StopwordsRegistry, RegistryException
from ParseTree import Evaluator

from interfaces.IStopwords import StopwordsInterface

import parsers, normalizers
import storages, lexicons, splitters, stop_words

import indexsupport
import PositionMap

from AccessControl.Permissions import  search_zcatalog
try:
    from AccessControl.Permissions import manage_zcatalog_indexes
except:
    manage_zcatalog_indexes = 'Manage ZCatalogIndex Entries' 


class TXNGError(Exception): pass


# Precalculate the term weight for terms derived by
# right truncation. The weight is calculated by the difference
# of the length of original term and the derived term.
# The weight is inverse proportional to difference
#
# weight = 1.0 / (a * difference + 1)
# a = (1 - p) / (p * d)
# p is the weight for terms with a difference of d  
#
# We use p=0.5 and  d=5


TRUNC_WEIGHT = {}
p = 0.5; d = 5
a = (1 - p) / (p * d)
for i in range(250): TRUNC_WEIGHT[i] = 1.0 / (a*i + 1)


class TextIndexNG(SimpleItem):
    """ TextIndexNG """

    meta_type = 'TextIndexNG2'
    __implements__ = PluggableIndex.PluggableIndexInterface

    security = ClassSecurityInfo()
    security.declareObjectProtected(manage_zcatalog_indexes)

    manage_options= (
        {'label': 'Settings',     
         'action': 'manage_workspace',
         'help': ('TextIndexNG','TextIndexNG_Settings.stx')},
        {'label': 'Stop words',     
         'action': 'manage_stopwords',
         'help': ('TextIndexNG','TextIndexNG_Stopwords.stx')},
        {'label': 'Normalizer',     
         'action': 'manage_normalizer',
         'help': ('TextIndex','TextIndexNG_Normalizer.stx')},
        {'label': 'Converters',     
         'action': 'manage_converters',
         'help': ('TextIndexNG','TextIndexNG_Converters.stx')},
        {'label': 'Vocabulary',     
         'action': 'manage_vocabulary',
         'help': ('TextIndexNG','TextIndexNG_Vocabulary.stx')},
        {'label': 'Test',     
         'action': 'manage_test',
         'help': ('TextIndexNG','TextIndexNG_Test.stx')},
        {'label': 'Statistics',     
         'action': 'manage_statistics',
         'help': ('TextIndexNG','TextIndexNG_Statistics.stx')},
    )

    _all_options = ('splitter_max_len', 'use_splitter', "splitter_separators",
         'splitter_single_chars', 'splitter_casefolding', 
         'lexicon', 'near_distance', 'truncate_left', 'autoexpand',
         'autoexpand_limit', 'numhits', 'use_storage', 'use_thesaurus', 'thesaurus_mode',
         'use_stopwords', 'use_normalizer', 'use_converters',
         'use_parser', 'indexed_fields', 'default_encoding'
        )

    query_options = ("query", "operator", "parser", "encoding", 'near_distance', 'autoexpand',
                     'numhits')

    def __init__(self, id, extra=None, caller=None):

        def _get(o, k, default):
            """ return a value for a given key of a dict/record 'o' """
            if isinstance(o, dict):
                return o.get(k, default)
            else:
                return getattr(o, k, default)
        
        self.id = id

        # check parameters
        if extra:
            for k in extra.keys():
                if not k in self._all_options:
                    raise TXNGError,'unknown parameter "%s"' % k

        if caller is not None:
            self.catalog_path = '/'.join(caller.getPhysicalPath())
        else:
            self.catalog_path = None

        # indexed attributes
        self._indexed_fields = _get(extra, 'indexed_fields', '').split(',')
        self._indexed_fields = [ attr.strip() for attr in  self._indexed_fields if attr ]
        if not self._indexed_fields:
            self._indexed_fields = [ self.id ]

        # splitter to be used
        self.use_splitter = _get(extra, 'use_splitter', 'TXNGSplitter')

        # max len of splitted words
        self.splitter_max_len= _get(extra, 'splitter_max_len', 64)

        # allow single characters
        self.splitter_single_chars = _get(extra,'splitter_single_chars',0)

        # valid word separators
        self.splitter_separators = _get(extra, 'splitter_separators','.+-_@')

        # allow single characters
        self.splitter_casefolding = _get(extra,'splitter_casefolding',1) 

        # left truncation
        self.truncate_left = _get(extra, 'truncate_left', 0)

        # Term autoexpansion
        self.autoexpand = _get(extra, 'autoexpand', 0)
        self.autoexpand_limit = _get(extra, 'autoexpand_limit', 4)

        # maximum number of hits
        self.numhits = _get(extra, 'numhits', 999999999)

        # default maximum distance for words with near search
        self.near_distance = _get(extra,'near_distance', 5)

        # Stopwords: either filename or StopWord object
        self.use_stopwords = _get(extra, 'use_stopwords', None) or None
        if self.use_stopwords:
            verifyClass(StopwordsInterface, self.use_stopwords.__class__)
     
        # Normalizer
        self.use_normalizer = _get(extra,'use_normalizer', None) or None

        # use converters from the ConvertersRegistry
        self.use_converters = _get(extra,'use_converters',0) 

        # Storage to be used
        self.use_storage = _get(extra,'use_storage', 'StandardStorage') 

        # encoding
        self.default_encoding = _get(extra,'default_encoding', 'iso-8859-15') 

        # check Parser
        self.use_parser = _get(extra, 'use_parser','PyQueryParser')
        
        # Thesaurus
        self.use_thesaurus = _get(extra, 'use_thesaurus', None)
        self.thesaurus_mode = _get(extra, 'thesaurus_mode', None)

        self.use_lexicon = 'StandardLexicon'
        self.clear()


    def clear(self):
        self._storage = StorageRegistry.get(self.use_storage)() 
        self._lexicon = LexiconRegistry.get(self.use_lexicon)(truncate_left=self.truncate_left)

    def getId(self):   return self.id
    def __len__(self): return len(self._storage)
    def __nonzero__(self): return not not self._unindex
    def getLexicon(self): return self._lexicon
    def getStorage(self): return self._storage

    def index_object(self, documentId, obj, threshold=None):
        """ wrapper to handle indexing of multiple attributes """
        # needed for backward compatibility
        try: fields = self._indexed_fields
        except: fields  = [ self.id ]

        res = 0
        all_wids = []
        for attr in fields:
            try:
                wids = self._index_object(documentId, obj, threshold, attr)
                if wids is not None:
                    all_wids.extend(wids)
            except:
                pass

        # get rid of words removed by reindexing
        try:
            o_wids = IISet(self._storage.getWordIdsForDocId(documentId))
        except KeyError:
            o_wids = IISet()

        all_wids_set = IISet(all_wids)
        remove_wids = difference(o_wids, all_wids_set)
        insert_wids = difference(all_wids_set, o_wids)
        insert_dict = {}   # hash wids to dict for performance reasons
        for wid in insert_wids.keys(): insert_dict[wid] = 1

        if len(remove_wids) > 0:
            self._storage.removeWordIdsForDocId(documentId, remove_wids) 
        if all_wids:
            self._storage.insert([w for w in all_wids if insert_dict.has_key(w)], documentId)
        return len(all_wids)
        
    def _index_object(self, documentId, obj, threshold=None, attr=''):

        encoding = self.default_encoding
        source = mimetype = None

        # This is to support foreign file formats that
        # are stored as "File" objects when searching
        # through PrincipiaSearchSource

        if hasattr(obj, 'txng_get'):
            # Check if the object has a method txng_get()
            result = obj.txng_get([attr])
            if result is None: return None
            source, mimetype, encoding = result

        elif obj.meta_type in ('File', 'Portal File') and  \
           attr in ('PrincipiaSearchSource', 'SearchableText'):

            source= getattr(obj, attr, None)
            if source and not self.use_converters:
                if callable(source): source = source()
            else:              
                source = str(obj)
            mimetype = obj.content_type

        elif obj.meta_type == 'ExtFile' and \
           attr in ('PrincipiaSearchSource', 'SearchableText'):
            source = obj.index_html()
            mimetype = obj.getContentType()

        elif obj.meta_type in ('ZMSFile',):
            lang = attr[attr.rfind('_')+1:]
            req = {'lang' : lang}
            file = obj.getObjProperty('file', req)
            source = ''
            mimetype = None
            if file:
                source = file.getData()
                mimetype = file.getContentType()
   
        elif obj.meta_type in ('TTWObject',) and attr not in ('SearchableText', ): 
            field = obj.get(attr)
            source = str(field)
            if field.meta_type in ( 'ZMSFile', 'File' ):
                mimetype = field.getContentType()
            else:
                mimetype = None

        else:
            # default behaviour: try to obtain the source from
            # the attribute or method call return value

            try:
                source = getattr(obj, attr)
                if callable(source): source = source()
                if not isinstance(source, unicode):
                    source = str(source)
            except (AttributeError, TypeError):
                return None
        
        # If enabled, we try to find a valid document converter
        # and convert the data to get a hopefully text only representation
        # of the data.

        if self.use_converters:
            if mimetype is None or mimetype == 'application/octet-stream':
                mimetype, encoding = guess_content_type(obj.getId(), source)
                if not encoding:
                    encoding = self.default_encoding

            try: 
                converter = ConverterRegistry.get(mimetype)
            except RegistryException: 
                LOG('textindexng', ERROR, '%s could not be converted because no converter could be found for %s' % (obj.absolute_url(1), mimetype))
                return None

            if converter:
                try:
                    source, encoding = converter.convert2(source, encoding, mimetype)
                except:
                    try:
                        source = converter.convert(source)
                    except:
                        LOG('textindexng', ERROR, '%s could not be converted' % obj.absolute_url(1), error=sys.exc_info())
                        return None

            if obj.meta_type == 'Portal File': 
                source += ' ' + obj.SearchableText()

        # Now we try to get a valid encoding. For unicode strings
        # we have to perform no action. For string objects we check
        # if the document has an attibute (not a method) '<index>_encoding'.
        # As fallback we also check for the presence of an attribute
        # 'document_encoding'. Checking for the two attributes allows
        # us to define different encodings for different attributes
        # on an object. This is useful when an object stores multiple texts
        # as attributes within the same instance (e.g. for multilingual
        # versions of a text but with different encodings). 
        # If no encoding is specified as object attribute, we will use
        # Python's default encoding.
        # After getting the encoding, we convert the data to unicode.

        if isinstance(source, str):
            if encoding is None:
                try: encoding = self.default_encoding
                except: encoding = self.default_encoding = 'iso-8859-15'

                for k in ['document_encoding', attr + '_encoding']:
                    enc = getattr(obj, k, None)
                    if enc is not None: encoding = enc  

            if encoding=='ascii': encoding ='iso-8859-15'         
            try:
                source = unicode(source, encoding, 'strict')
            except UnicodeDecodeError:
                LOG('textindexng', WARNING, 'UnicodeDecodeError raised from %s - ignoring unknown unicode characters'  % obj.absolute_url(1))
                source = unicode(source, encoding, 'ignore')
 
        elif isinstance(source, unicode):  pass
        else: raise TXNGError,"unknown object type" 

        source = source.strip()
        if not source: return None

        # Normalization: apply translation table to data
        if self.use_normalizer:
            source = NormalizerRegistry.get(self.use_normalizer).process(source)    
 
        # Split the text into a list of words
        SP = SplitterRegistry.get(self.use_splitter)

        _source = source
        words = SP(casefolding  = self.splitter_casefolding,
                   separator    = self.splitter_separators,
                   maxlen       = self.splitter_max_len,
                   singlechar   = self.splitter_single_chars
                   ).split(_source)

        #  remove stopwords from data
        if self.use_stopwords:
            words = self.use_stopwords.process( words ) 

        # We pass the list of words to the corresponding lexicon
        # and obtain a list of wordIds. The "old" TextIndex iterated
        # over every single words (overhead).
        return self._lexicon.getWordIdList(words)

    def unindex_object(self, documentId): 
        """ carefully unindex document with Id 'documentId'
            index and do not fail if it does not exist 
        """
        self._storage.removeDocument(documentId)

    def _apply_index(self, request, cid=''): 
        """ Apply the index to query parameters given in the argument,
        request

        The argument should be a mapping object.

        If the request does not contain the needed parameters, then
        None is returned.
 
        Otherwise two objects are returned.  The first object is a
        ResultSet containing the record numbers of the matching
        records.  The second object is a tuple containing the names of
        all data fields used.  
        """

        record = parseIndexRequest(request, self.id, self.query_options)
        if record.keys==None: return None

        # extract some parameters from the request 

        query_operator = record.get('operator','dummy')
        if query_operator is None:
            raise TXNGError, ("Invalid operator '%s' "
                                            "for a TextIndex" % query_operator)

        query_parser = record.get('parser', self.use_parser)
        if not ParserRegistry.is_registered(query_parser): 
            raise TXNGError, "Unknown parser '%s'" %  query_parser

 
        query = record.keys[0]
        encoding = record.get('encoding', self.default_encoding)
        if isinstance(query, str): query = unicode(query, encoding)
        P = ParserRegistry.get( query_parser )
        parsed_query = P(query.strip(), operator=query_operator)
        if not parsed_query:
            raise TXNGError,"Bad query: '%s'" % q

        evaluator = Evaluator(self)
        evaluator.autoexpand = record.get('autoexpand', self.autoexpand)
        evaluator.near_distance = record.get('near_distance', self.near_distance)

        numhits = record.get('numhits', self.numhits)
        resultset = evaluator(parsed_query)

        if self.getStorage().providesWordFrequencies():
            resultset.cosine_ranking(self, numhits)
            return  resultset.result(), (self.id,) 
        else:
            return  resultset.docIds(), (self.id,) 
            


    ################################################################
    # callbacks for ParseTree.py
    ################################################################

    def _lookup(self, words, do_autoexpand=1):
        """ search a word or a list of words in the lexicon and 
            return a ResultSet of found documents.
        """

        docids = IISet()
        used_words = {} 

        #  remove stopwords from data
        if self.use_stopwords:
            words = self.use_stopwords.process( words ) 

        if self.use_thesaurus and self.thesaurus_mode == 'expand_always':
            TH = ThesaurusRegistry.get(self.use_thesaurus)
            for word in words[:]:
                r = TH.getTermsFor(word)
                words.extend(r)

        for word in words:

            # perform casefolding if necessary
            if self.splitter_casefolding:
                word = word.lower()

            if self.use_normalizer:
                word = NormalizerRegistry.get(self.use_normalizer).process(word)    
 
            used_words[word] = 1.0

            wid = self._lexicon.getWordId(word)

            # Retrieve list of docIds for this wordid
            if wid is not None:
                docids.update( self._storage.get(wid) )

            # perform autoexpansion of terms by performing
            # a search using right-truncation
            if do_autoexpand and self.autoexpand and len(word) >= self.autoexpand_limit:
                rs = self.lookupWordsByTruncation(word, right=1)
                docids.update(rs.docIds())
                wlen = len(word)
                for w in rs.words().keys():
                    used_words[w] = TRUNC_WEIGHT[len(w)-wlen]

        return ResultSet(docids, used_words)

    
    def lookupWord(self, word):
        """ search a word in the lexicon and return a ResultSet
            of found documents 
        """

        return self._lookup( [word] )


    def lookupWordsByPattern(self,word):
        """ perform full pattern matching """

        if self.splitter_casefolding: word = word.lower()
        words = self._lexicon.getWordsForPattern(word)

        return self._lookup(words, do_autoexpand=0)

    def lookupWordsByTruncation(self, word, left=0, right=0):
        """ perform right truncation lookup"""

        if self.use_normalizer:
            word = NormalizerRegistry.get(self.use_normalizer).process(word)    

        if self.splitter_casefolding: word = word.lower()
        if right:
            words = self._lexicon.getWordsForRightTruncation(word)
        if left:
            if  self.truncate_left:
                words = self._lexicon.getWordsForLeftTruncation(word)
            else: 
                raise TXNGError, "Left truncation not allowed"

        return self._lookup(words, do_autoexpand=0)


    def lookupRange(self, w1, w2):
        """ search all words between w1 and w2 """

        if self.splitter_casefolding: 
            w1 = w1.lower()
            w2 = w2.lower()

        words = self._lexicon.getWordsInRange(w1, w2)
        return self._lookup(words, do_autoexpand=0)


    def lookupWordsBySimilarity(self, word):       
        """ perform a similarity lookup """

        lst = self._lexicon.getSimiliarWords(word)

        docids = IISet()
        used_words = {} 

        getwid = self._lexicon.getWordId

        for word, threshold in lst:
            used_words[word] = threshold
            wid = getwid(word)

            docids.update( self._storage.get(wid) )

        return ResultSet(docids, used_words)


    def lookupWordsBySubstring(self, word):       
        """ perform a substring search """

        if self.splitter_casefolding: word = word.lower()
        words = self._lexicon.getWordsForSubstring(word)
        return self._lookup(words, do_autoexpand=0)
        

    ###################################################################
    # document lookup for near and phrase search 
    ###################################################################

    def positionsFromDocumentLookup(self,docId, words):
        """ search all positions for a list of words for
            a given document given by its documentId.
            positions() returns a mapping word to
            list of positions of the word inside the document.
        """

        # some query preprocessing  
        if self.splitter_casefolding:
            words = [word.lower() for word in words] 

        posMap = PositionMap.PositionMap() 

        # obtain wids from document
        wids = self._storage.getWordIdsForDocId(docId)
        word_lst = [self._lexicon.getWord(wid) for wid in wids] 
        for word in words:
            posLst = indexsupport.listIndexes(word_lst, word)        
            posMap.append(word, IISet(posLst) )

        return posMap

    ###################################################################
    # some helper functions 
    ###################################################################

    def numObjects(self):
        """ return number of index objects """
        return len(self._storage.getDocIds())

    def rebuild(self):
        """ rebuild the inverted index """
        self._storage.buildInvertedIndex()
        return "done"

    def info(self):
        """ return a list of TextIndexNG properties """

        lst = [ (k,str(getattr(self,k))) for k in dir(self) ] 
        lst.sort()
        return lst

    def getEntryForObject(self, docId, default=None):
        """Get all information contained for a specific object.
           This takes the objects record ID as it's main argument.
        """

        try:
            # use an IISet() here to iterate over a unique list
            # of wids 
            wids = IISet(self._storage.getWordIdsForDocId(docId))
            return [(self._lexicon.getWord(wid), self._storage.getWordFrequency(docId, wid)) for wid in wids]
        except:
            return []

    def getRegisteredObjectForObject(self, docId, default=None):
        """Get all information contained for a specific object.
           This takes the objects record ID as it's main argument.
        """

        return "%d distinct words" % \
            len(self._storage.getWordIdsForDocId( docId ))

    def uniqueValues(self, name=None, withLengths=0):
        """ we don't implement that ! """
        raise NotImplementedError

    ###################################################################
    # minor introspection API
    ###################################################################

    def allSettingOptions(self):
        return self._all_options


    def getSetting(self, key):
        if not key in self._all_options:
            raise TXNGError, "No such setting '%s'" % key

        return getattr(self, key, '')

    def getIndexSourceNames(self):
        """ return sequence of indexed attributes """
        
        try:
            return self._indexed_fields
        except:
            return [ self.id ]


    ###################################################################
    # Stopword handling
    ###################################################################

    def getStopWords(self):     
        """ return a list of all stopwords (for ZMI) """

        if self.use_stopwords:
            return self.use_stopwords.getStopWords()
        else:
            return []

    ###################################################################
    # Normalizer handling
    ###################################################################

    def getNormalizerTable(self):     
        """ return the normalizer translation table """
        
        if self.use_normalizer:       
            return NormalizerRegistry.get(self.use_normalizer).getTable()
        else:
            return None

    ###################################################################
    # Converters
    ###################################################################

    def allConverters(self):
        """ return a list of all registered converters """
        lst = []
        used = []
        converters = ConverterRegistry.allRegisteredObjects()
        converters.sort( lambda x,y: cmp(x.getType(),y.getType()) )
        for c in converters:
            if not c in used:
                used.append(c)
                lst.append( (c.getType(), c.getDescription(), c.getDependency() ) )

        return lst

    ###################################################################
    # Testing 
    ###################################################################

    def testTextIndexNG(self, query, parser, operator=None):
        """ test the TextIndexNG """
        
        res = self._getCatalog().searchResults({self.id: {'query': query,
                                                          'parser': parser,
                                                          'operator': operator} })

        return [r.getURL(relative=1) for r in res]


    ###################################################################
    # Vocabulary browser 
    ###################################################################

    def _getCatalog(self):
        """ return the Catalog instance """

        try: 
            self._v_catalog = self.restrictedTraverse(self.catalog_path)
        except KeyError:
            self._v_catalog = self.aq_parent.aq_parent
        return self._v_catalog

    def getDocumentsForWord(self, word):
        """ return a sequence of document paths that contain 'word' """

        catalog = self._getCatalog()

        wid = self._lexicon.getWordId(word)
        docIds = self._storage.getDocumentIdsForWordId(wid)
        paths =  [ catalog.getpath(docId) for docId in docIds ]
        paths.sort()
        return paths

    ###################################################################
    # Cleanup vocabulary
    ###################################################################

    def manage_cleanVocabulary(self):
        """ cleanup the vocabulary """

        wids = list(self._lexicon.getWordIds())
        for wid in wids:
            docids = self._storage.getDocumentIdsForWordId(wid)
            if not docids:
                self._lexicon.removeWordId(wid)

        return 'Vocabulary cleaned'

    ###################################################################
    # TextIndexNG preferences 
    ###################################################################

    def manage_setPreferences(self,extra, debug_mode,
                               REQUEST=None,RESPONSE=None,URL2=None):
        """ preferences of TextIndex """

        for x in ('near_distance', ): 

            if hasattr(extra,x):

                oldval = getattr(self,x)
                newval = getattr(extra,x)
                setattr(self, x, newval)

        if RESPONSE:
            RESPONSE.redirect(URL2 + 
                '/manage_main?manage_tabs_message=Preferences%20saved')

    def manage_checkIndex1(self):
        """ check index (only for internal tests) """
      
        # check lexikon
        fwidx = self._lexicon._forward_idx
        revidx = self._lexicon._inverse_idx
        all_wids = fwidx.values()
        assert len(fwidx) == len(revidx) 
        for word, wid in fwidx.items():
            assert revidx[wid] == word

        # check storage
        fwidx = self._storage._forward_idx
        revidx = self._storage._reverse_idx

        all_docids = revidx.keys()
        for wid,docids in fwidx.items():
            assert wid in all_wids
            for docid in (isinstance(docids, int) and [docids] or docids.keys()):
                assert docid in all_docids

        for docid in revidx.keys():
            for wid in self._storage.getWordIdsForDocId(docid):
                assert wid in all_wids
        return 'Index seems to be consistent'


    manage_workspace  = DTMLFile("dtml/manageTextIndexNG",globals())
    manage_stopwords  = DTMLFile("dtml/manageStopWords",globals())
    manage_normalizer = DTMLFile("dtml/manageNormalizer",globals())
    manage_converters = DTMLFile("dtml/showConverterRegistry",globals())
    manage_vocabulary = DTMLFile("dtml/vocabularyBrowser",globals())
    manage_statistics = DTMLFile("dtml/manageStatistics",globals())
    showDocuments     = DTMLFile("dtml/vocabularyShowDocuments",globals())
    manage_test       = DTMLFile("dtml/testTextIndexNG",globals())
    testResults       = DTMLFile("dtml/testResults",globals())

InitializeClass(TextIndexNG)


manage_addTextIndexNGForm = DTMLFile('dtml/addTextIndexNG', globals())

def manage_addTextIndexNG(self, id, extra, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a new TextIndexNG """

    from Registry import StopwordsRegistry

    # the ZMI passes the name of a registered Stopwords object (usually the
    # language abreviation like 'en', 'de'. 

    if extra.use_stopwords:
        sw = StopwordsRegistry.get(extra.use_stopwords)
        extra.use_stopwords = sw

    return self.manage_addIndex(id, 'TextIndexNG2', extra, REQUEST, RESPONSE, URL3)

