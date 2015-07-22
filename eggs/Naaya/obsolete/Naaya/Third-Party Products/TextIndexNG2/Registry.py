###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
Registry  for all and everything 

$Id: Registry.py,v 1.24 2004/12/28 10:54:15 ajung Exp $
"""

import sys
from types import InstanceType

from zLOG import WARNING, LOG
from classVerify import verifyClass
from interfaces.IRegistry import RegistryInterface

class RegistryException(Exception): pass

class Registry:
    """registry for data"""   

    __implements__ = RegistryInterface
    
    def __init__(self, id, ifaces=None):
        self.id = id
        self.ifaces = [] 
        self.data = {}
        if ifaces: 
            if not isinstance(ifaces, tuple): ifaces = [ ifaces ]
            self.ifaces.extend(ifaces) 

 
    def __call__(self, *args, **kw):
        """ emulate a singleton behaviour """
        return self 

    def getRegisteredObject(self, id):

        if not self.data.has_key(id):
            raise RegistryException, \
            '"%s" not registered in registry "%s"' % (id, self.id)

        return self.data[id] 

    get = getRegisteredObject

    def is_registered(self, id):
        return self.data.has_key(id)

    def register(self, id, instance=None):
        """ map an id to an instance """
        if self.data.has_key(id):
            pass
            #raise RegistryException, '"%s" already registered' % id
        
        for iface in self.ifaces:
            try:
                if isinstance(instance, InstanceType):
                    verifyClass(iface, instance.__class__)
                else:
                    verifyClass(iface, instance)

            except:
                LOG('TextIndexNG', WARNING, 
                    'interface broken for %s' % str(instance),
                    error=sys.exc_info())
                raise
    
        self.data[id] = instance


    def unregister(self, id):
        """ delete an item """
        del self.data[id]


    def clear(self):
        self.data = {}

    def allRegisteredObjects(self):
        return self.data.values()

    def allIds(self):
        return self.data.keys()


from interfaces.IConverter import ConverterInterface
from interfaces.ILexicon import LexiconInterface
from interfaces.INormalizer import NormalizerInterface
from interfaces.IParser import ParserInterface
from interfaces.IStopwords import StopwordsInterface
from interfaces.IStorage import StorageInterface
from interfaces.IThesaurus import IThesaurus

class ConverterRegistry(Registry):
    """ registry for converters """    
ConverterRegistry = ConverterRegistry('converters', (ConverterInterface,) )

class LexiconRegistry(Registry):
    """registry for Lexicons"""    
LexiconRegistry = LexiconRegistry('lexicons', (LexiconInterface,) )

class NormalizerRegistry(Registry):
    """registry for Normalizer """    
NormalizerRegistry = NormalizerRegistry('Normalizer', NormalizerInterface )

class ParserRegistry(Registry):
    """registry for parsers"""    
ParserRegistry = ParserRegistry('parsers', (ParserInterface,) )

class SplitterRegistry(Registry):
    """registry for Splitter"""    
SplitterRegistry = SplitterRegistry('Splitter' )

class StopwordsRegistry(Registry):
    """registry for Stopwords """    
StopwordsRegistry = StopwordsRegistry('Stopwords', StopwordsInterface )

class StorageRegistry(Registry):
    """registry for storages """    
StorageRegistry = StorageRegistry('storages', (StorageInterface,) )

class ThesaurusRegistry(Registry):
    """registry for thesauruses """
ThesaurusRegistry = ThesaurusRegistry('thesaurus', (IThesaurus,))
