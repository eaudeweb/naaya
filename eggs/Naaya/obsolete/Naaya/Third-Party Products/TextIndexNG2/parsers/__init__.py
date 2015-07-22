###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

from Products.TextIndexNG2.Registry import ParserRegistry

import PyQueryParser
import DumbQueryParser
import GermanQueryParser
import FrenchQueryParser

ParserRegistry.register('PyQueryParser', PyQueryParser.Parser())
ParserRegistry.register('DumbQueryParser', DumbQueryParser.Parser())
ParserRegistry.register('GermanQueryParser', GermanQueryParser.Parser())
ParserRegistry.register('FrenchQueryParser', FrenchQueryParser.Parser())
