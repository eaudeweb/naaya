###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

import Interface

class IThesaurus(Interface.Base):
    """ interface for a thesaurus"""

    def getTermsFor(word):
        """ returns either a sequence of similar terms for 'word' or a sequence
            of tuples (term, weight) where 'term' is similiar to 'word' and 'weight'
            is a float between 0.0 and 1.0 measuring the similiarity of 'term' to 'word'
        """    
