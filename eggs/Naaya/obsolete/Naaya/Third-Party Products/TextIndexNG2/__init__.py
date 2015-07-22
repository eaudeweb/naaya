###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

# some ZCatalog monkey patching

import os, sys

if not sys.version_info > (2,3,3):
    raise RuntimeError('This version of TextIndexNG requires Python 2.3.3+')

package_home = os.path.dirname(__file__)
if not package_home in sys.path:
    sys.path.append(package_home)


def getEntriesFromRegistry(self, id):
    """ get infos from a TXNG registry """

    from Products.TextIndexNG2.Registry import LexiconRegistry
    from Products.TextIndexNG2.Registry import ConverterRegistry
    from Products.TextIndexNG2.Registry import NormalizerRegistry
    from Products.TextIndexNG2.Registry import ParserRegistry
    from Products.TextIndexNG2.Registry import SplitterRegistry
    from Products.TextIndexNG2.Registry import StopwordsRegistry
    from Products.TextIndexNG2.Registry import StorageRegistry
    from Products.TextIndexNG2.Registry import ThesaurusRegistry

    registry = None 

    try:
        registry = vars()['%sRegistry' % id]
    except:
        import traceback
        traceback.print_exc()
        raise

    keys = registry.allIds()
    keys.sort()
    return [(k, registry.getRegisteredObject(k)) for k in keys] 


try:
    import normalizer, indexsupport
except ImportError:
    from zLOG import LOG, ERROR
    LOG("TextIndexNG",ERROR,"Import of Python extensions failed")
    


def initialize(context):
    from Products.TextIndexNG2 import TextIndexNG

    manage_addTextIndexNGForm = TextIndexNG.manage_addTextIndexNGForm 
    manage_addTextIndexNG     = TextIndexNG.manage_addTextIndexNG
    
    context.registerClass( 
        TextIndexNG.TextIndexNG,
        permission='Add Pluggable Index', 
        constructors=(manage_addTextIndexNGForm,
        manage_addTextIndexNG),
        icon='www/index.gif',
        visibility=None
        )

    context.registerHelp()
    context.registerHelpTitle("Zope Help")

    from Products.ZCatalog.ZCatalog import ZCatalog
    ZCatalog.getEntriesFromRegistry = getEntriesFromRegistry

    import converters
    import thesaurus


# Indicate if we should omit register 2nd-level components
fast_startup = int(os.environ.get('TXNG_FASTSTARTUP', 0))

################################################################
# Register with CMF/Plone
################################################################

textindexng_globals = globals()

try:
    from Products.CMFCore.DirectoryView import registerDirectory
    registerDirectory('skins', textindexng_globals)
except ImportError:
    pass
