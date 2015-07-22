"""
Version: $Id: babelizer.py,v 1.4 2001/06/04 21:25:09 Administrator Exp $
Author: Jonathan Feinberg <jdf@pobox.com>
"""

import re, string, urllib2, urllib, sys

"""
Various patterns I have encountered in looking for the babelfish result.
We try each of them in turn, based on the relative number of times I've
seen each of these patterns.  $1.00 to anyone who can provide a heuristic
for knowing which one to use.   This includes AltaVista employees.
"""

__where = [ re.compile(r'name=\"q\">([^<]*)'),
            re.compile(r'td bgcolor=white>([^<]*)'),
            re.compile(r'<\/strong><br>([^<]*)'),
            re.compile(r'<div style=padding:10px;>([^<]*)'),
          ]

#__languages = { 'english'   : 'en',
#                'french'    : 'fr',
#                'spanish'   : 'es',
#                'german'    : 'de',
#                'italian'   : 'it',
#                'portugese' : 'pt',
#                'russian'   : 'ru',
#                'greek'     : 'el',
#              }

# All of the available language names.
#available_languages = [ x.title() for x in __languages.keys() ]

# Calling translate() or babelize() can raise a BabelizerError
class BabelizerError(Exception):
    pass

class LanguageNotAvailableError(BabelizerError):
    pass

class BabelfishChangedError(BabelizerError):
    pass

class BabelizerIOError(BabelizerError):
    pass


def clean(text):
    return ' '.join(string.replace(text.strip(), "\n", ' ').split())

def stripMSWordLatin1(s):
    """ replace MSWord characters """
    s = s.replace('\x85', '...') #ellipsis
    s = s.replace('\x96', '-')   #long dash
    s = s.replace('\x97', '-')   #long dash
    s = s.replace('\x91', '\'')  #single quote opening
    s = s.replace('\x92', '\'')  #single quote closing
    s = s.replace('\x93', '"')  #double quote opening
    s = s.replace('\x94', '"')  #double quote closing
    s = s.replace('\x95', '*')  #dot used for bullet points
    return s

def stripMSWordUTF8(s):
    """ replace MSWord characters """
    if isinstance(s, unicode): s = s.encode('utf-8')
    s = s.replace('\\xe2\\x80\\xa6', '...') #ellipsis
    s = s.replace('\\xe2\\x80\\x93', '-')   #long dash
    s = s.replace('\\xe2\\x80\\x94', '-')   #long dash
    s = s.replace('\\xe2\\x80\\x98', '\'')  #single quote opening
    s = s.replace('\xe2\x80\x99', '\'')  #single quote closing
    s = s.replace('\\xe2\\x80\\x9c', '"')  #single quote closing
    s = s.replace('\\xe2\\x80\\x9d', '"')  #single quote closing
    s = s.replace('\\xe2\\x80\\xa2', '*')  #dot used for bullet points
    return s

def translate(phrase, from_lang, to_lang):
    phrase = clean(phrase)
#    try:
#        from_code = __languages[from_lang.lower()]
#        to_code = __languages[to_lang.lower()]
#    except KeyError, lang:
#        raise LanguageNotAvailableError(lang)

    req = urllib2.Request('http://babelfish.altavista.com/babelfish/tr')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')

    params = urllib.urlencode( { 'BabelFishFrontPage' : 'yes',
                                 'doit' : 'done',
                                 'intl' : '1',
                                 'tt' : 'urltext',
                                 'urltext': stripMSWordUTF8(phrase),
                                 'lp' : from_lang + '_' + to_lang } )

    try:
        response = urllib2.urlopen(req, params)
    except IOError, what:
        raise BabelizerIOError("Couldn't talk to server: %s" % what)
    except:
        print "Unexpected error:", sys.exc_info()[0]

    html = response.read()
    try:
        begin = html.index('<!-- Target text (content) -->')
        end = html.index('<!-- end: Target text (content) -->')
        html = html[begin:end]
    except ValueError:
        pass
    for regex in __where:
        match = regex.search(html)
        if match: break
    if not match: raise BabelfishChangedError("Can't recognize translated string.")
    return clean(match.group(1))

def babelize(phrase, from_language, through_language, limit = 12, callback = None):
    phrase = clean(phrase)
    seen = { phrase: 1 }
    results = []
    if callback:
        def_callback = callback
    else:
        def_callback = results.append
    def_callback(phrase)
    flip = { from_language: through_language, through_language: from_language }
    next = from_language
    for i in range(limit):
        phrase = translate(phrase, next, flip[next])
        if seen.has_key(phrase):
            break
        seen[phrase] = 1
        def_callback(phrase)
        next = flip[next]
    # next is set to the language of the last entry.  this should be the same
    # as the language we are translating to
    if next != through_language:
        phrase = translate(phrase, next, flip[next])
        def_callback(phrase)
    if not callback:
        return results