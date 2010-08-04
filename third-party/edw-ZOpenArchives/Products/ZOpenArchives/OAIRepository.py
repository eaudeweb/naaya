import DateTime
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from App.Management import Navigation
from Globals import Persistent
from OFS.Folder import Folder, manage_addFolder
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from zope import interface

from interfaces import IOAIRepository
from OAINamespace import manage_addOAINamespace
from OAIToken import OAIToken
from utils import Empty

DEFAULTS = {
    'document': 'index_html',
    'catalog': 'oai_catalog',
    'tokens_folder': 'tokens',
    'namespaces_folder': 'namespaces',
    'encoding': 'utf-8'
}

class OAIRepository(Navigation, Folder, Persistent, Implicit):
    """ This class is extended by OAIServer and OAIAggregator """
    interface.implements(IOAIRepository)

    manage_options = (
        {'label': 'Contents', 'action': 'manage_main'},
        {'label': 'Preferences', 'action': 'manage_preferences' },
        {'label': 'Update','action': 'manage_update'},
    )
    security = ClassSecurityInfo()

    security.declarePrivate('initialize')
    def initialize(self):
        """ Adding a catalog with needed indexes and other stuff """
        catalog_id = DEFAULTS['catalog']
        manage_addZCatalog(self, catalog_id, 'Default catalog')
        catalog_ob = self._getOb(catalog_id)

        #Add Lexicon
        elem = []
        wordSplitter = Empty()
        wordSplitter.group = 'Locale Aware Word Splitter'
        wordSplitter.name = 'Locale Aware Word Splitter'

        caseNormalizer = Empty()
        caseNormalizer.group = 'Case Normalizer'
        caseNormalizer.name = 'Case Normalizer'

        stopWords = Empty()
        stopWords.group = 'Stop Words'
        stopWords.name = 'Remove listed and single char words'

        accentRemover = Empty()
        accentRemover.group = 'Accent Normalizer'
        accentRemover.name = 'Accent Normalizer'

        elem.append(wordSplitter)
        elem.append(caseNormalizer)
        elem.append(stopWords)
        elem.append(accentRemover)

        try:
            catalog_ob.manage_addProduct['ZCTextIndex'].manage_addLexicon(
                'Lexicon', 'Default Lexicon', elem)
        except:
            pass

        self.add_indexes(catalog_ob)
        self.add_metadata(catalog_ob)

        #Add Token folder
        manage_addFolder(self, DEFAULTS['tokens_folder'], 'Token storage')
        #Add Namespace folder
        manage_addFolder(self, DEFAULTS['namespaces_folder'],
            'Namespace storage')
        #Add Dublic Core OAINamespace
        manage_addOAINamespace(self._getOb(DEFAULTS['namespaces_folder']))

    def update(self):
        """ Update OAITokens """
        results = self.getCatalog().searchResults({
            'meta_type': OAIToken.meta_type,
            'expiration': DateTime.DateTime().HTML4(),
            'expiration_usage':'range:max'
        })
        self.getTokenStorage().manage_delObjects(ids=[t.id for t in results])

    #security.declarePrivate('getStorage')
    #def getStorage(self):
    #    """ What type of storage """
    #    return self.storage

    security.declarePrivate('getCatalog')
    def getCatalog(self):
        """ Getting default catalog """
        return self._getOb(DEFAULTS['catalog'])

    def getTokenStorage(self):
        return self._getOb(DEFAULTS['tokens_folder'])

    security.declarePrivate('add_indexes')
    def add_indexes(self, catalog):
        """ """
        raise NotImplementedError

    security.declarePrivate('add_metadata')
    def add_metadata(self, catalog):
        """ """
        raise NotImplementedError

    security.declarePrivate('get_namespace_dict')
    def get_namespace_dict(self, name=""):
        """ """
        namespaces_folder_ob = self._getOb(DEFAULTS['namespaces_folder'])
        ns_ob = namespaces_folder_ob._getOb(name)
        return dict(ns_ob.get_dict())
