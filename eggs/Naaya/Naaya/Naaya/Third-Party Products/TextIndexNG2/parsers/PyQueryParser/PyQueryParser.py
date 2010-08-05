###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

#######################################################
# a new native Python QueryParser for TextIndexNG
# based on the QueryParser by Sidnei da Silva
#######################################################

import re
from Products.TextIndexNG2.BaseParser import BaseParser,QueryParserError
from Products.TextIndexNG2.ParseTree import *

class PhraseElements:
    """ wrapper class around a list to keep the nodes
        for a phrase search 
    """

    def __init__(self):
        self.clear()

    def addElement(self, item):
        self._list.insert(0, item)

    def getElements(self):
        return tuple(self._list)

    def clear(self):
        self._list = []


tokens = (
    'STRING' , 
    'NOT',
    'OR', 
    'AND', 
    'NEAR',
    'QUOTE',
    'OPENP', 
    'CLOSEP', 
)         

t_QUOTE     = r'\"'                   
t_OPENP     = r'\('           
t_CLOSEP    = r'\)'          
t_ignore    = '\t'

def t_NOT(t):
    'NOT\s+|not\s+|\-'
    return t

def t_AND(t):
    '\s+AND\s+|\s+and\s+'            
    return t

def t_OR(t):
    '\s+OR\s+|\s+or\s+'
    return t

def t_NEAR(t):
    '\s+NEAR\s+|\s+near\s+'
    return t
        
def t_STRING(t):
    r'[^()\s"]+' 
    return t

def t_newline(t):
    r'\n+'
    t.lineno += t.value.count("\n")
    
def t_error(t):
    
    if t.value[0] in [' ']:
        t.skip(1)
    else:
        raise QueryParserError,"Illegal character '%s'" % t.value[0]


# Build the lexer

import lex
lex.lex(debug=0)

def p_expr_parens(t):
    """expr :    OPENP expr CLOSEP """
    t[0] = t[2]

def p_expr_and(t):
    """expr :    expr AND expr """
    t[0] = AndNode( (t[1], t[3]) )

def p_expr_or(t):
    """expr :    expr OR expr """
    t[0] = OrNode( (t[1], t[3]) )

def p_expr_near(t):
    """expr :    expr NEAR expr """
    t[0] = NearNode( (t[1], t[3]) )

def p_expr_noop(t):
    """expr :    expr expr"""
    t[0] = AndNode( (t[1], t[2]))

def p_expr_expr_factor(t):
    """expr :  factor """
    t[0] = t[1]

def p_expr_expr_factor3(t):
    """expr :  NOT expr"""
    t[0] = NotNode( t[2] )

def p_expr_expr_factor2(t):
    """expr :  NOT factor """
    t[0] = NotNode( t[2] )

def p_factor_string(t):
    """factor : string"""
    t[0] = t[1]

def p_factor_quote(t):
    """factor :  quotestart qterm quoteend """
    t[0] = PhraseNode( phrase_elements.getElements() )

phrase_elements = PhraseElements()

def p_qterm_1(t):
    """ qterm : string qterm"""
    phrase_elements.addElement( t[1] )
    t[0] = [t[1], t[2]]
 
def p_qterm_2(t):
    """ qterm : string"""
    phrase_elements.addElement( t[1] ) 
    t[0] = t[1]

def p_quotestart_1(t):
    """ quotestart : QUOTE """
    phrase_elements.clear() 

def p_quoteend_1(t):
    """ quoteend : QUOTE """
    pass


# some regexes to distinguish between normal strings
# truncated strings and patterns

str_regex = re.compile(r'[^%*?()\s"]+$',re.LOCALE|re.UNICODE)
range_regex = re.compile(r'[^%*?()\s"]+\.\.[^%*?()\s"]+$',re.LOCALE|re.UNICODE)
sim_regex = re.compile(r'[%][^%*?()\s"]+$',re.LOCALE|re.UNICODE)
sub_regex = re.compile(r'[*][^%*?()\s"]+[*]$',re.LOCALE|re.UNICODE)
rt_regex  = re.compile(r'[^%*?()\s"]+[*]$',re.LOCALE|re.UNICODE)
lt_regex  = re.compile(r'[*][^%*?()\s"]+$',re.LOCALE|re.UNICODE)

def p_string(t):
    """string :  STRING
       | AND 
       | OR 
       | NEAR 
       | NOT"""
    if range_regex.match(t[1]): t[0] = RangeNode( tuple(t[1].split('..')) )
    elif str_regex.match(t[1]): t[0] = WordNode( t[1] )
    elif sim_regex.match(t[1]): t[0] = SimNode( t[1][1:] )
    elif sub_regex.match(t[1]): t[0] = SubstringNode( t[1][1:-1] )
    elif rt_regex.match(t[1]):  t[0] = TruncNode( t[1][:-1] )
    elif lt_regex.match(t[1]):  t[0] = LTruncNode( t[1][1:] )
    else:             
        if not (t[1].lower().strip() in ('and', 'or', 'not', 'near')):
            t[0] = GlobNode( t[1] )

 
def p_error(t):
    raise QueryParserError,"Syntax error at '%s'" % t.value

import yacc
try:
    yacc.yacc(debug=0)
except:
    from zLOG import LOG, ERROR
    LOG("TextIndexNG", ERROR, "parsetab creation failed") 


class Parser(BaseParser):

    id = 'NewQueryParser'
    parser_description = 'A TextIndex compatible parser (native Python version)'

    def parse(self, query, operator):
        
        try:
            return yacc.parse( query )
        except QueryParserError:
            raise 
        except:
            import traceback
            traceback.print_exc()
            raise QueryParserError, 'parser failed for query: %s' % query


def test():

    import os, re,traceback, atexit

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
            res = P(s)        
            print 'res:',res

        except:
            traceback.print_exc()


if __name__ == '__main__':
    test()
