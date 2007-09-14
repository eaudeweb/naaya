#!/usr/bin/env python2.1

###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

"""
DumbQueryParser class

A very dumb parser as temporarily solution for the non-yet-finished parser
"""


from Products.TextIndexNG2.BaseParser  import BaseParser, QueryParserError
from Products.TextIndexNG2.ParseTree import *

OperatorDict = {
    'or'        : 'txU',
    'and'       : 'txI',
    'near'      : 'txN',
    'quote'     : 'txQ'
}
 
class Parser(BaseParser):
    """Dumb query parser """ 

    def parse(self, query, operator):

        operator = operator.strip().lower()
        if not OperatorDict.has_key(operator):
            raise QueryParserError, 'unsupported operator: %s' % operator

        try:
            res = []
            words = [ x.strip() for x in query.split(' ')]

            for word in words:
                if word.startswith('%'):
                    res.append( SimNode(word[1:]) )
                else:
                    res.append( WordNode(word) )

            if operator=='and':     s = AndNode( res )
            elif operator=='or':    s = OrNode( res )
            elif operator=='near':  s = NearNode( res )
            elif operator=='quote': s = PhraseNode( res ) 

            return s 
        except:
            traceback.print_exc()
            raise QueryParserError,'parser failed for query: %s' % query


def test():

    import os, traceback, atexit

    histfile = os.path.expanduser('~/.pyhist')
    try:
        import readline
        readline.read_history_file(histfile)
        atexit.register(readline.write_history_file,histfile)
    except: pass

    print "entering interactive query mode:"
    while 1:

        s = raw_input('> ')
        print s  

        try:

            P = Parser()
            res = P.parse(s, 'and')        
            print 'res:',res

        except:
            traceback.print_exc()


if __name__ == '__main__':
    test()
