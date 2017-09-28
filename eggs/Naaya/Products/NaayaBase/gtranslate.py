import urllib
import urllib2
import simplejson

_GOOGLE_LANGUAGES = {
  'AFRIKAANS' : 'af',
  'ALBANIAN' : 'sq',
  'AMHARIC' : 'am',
  'ARABIC' : 'ar',
  'ARMENIAN' : 'hy',
  'AZERBAIJANI' : 'az',
  'BASQUE' : 'eu',
  'BELARUSIAN' : 'be',
  'BENGALI' : 'bn',
  'BIHARI' : 'bh',
  'BULGARIAN' : 'bg',
  'BURMESE' : 'my',
  'CATALAN' : 'ca',
  'CHEROKEE' : 'chr',
  'CHINESE' : 'zh',
  'CHINESE_SIMPLIFIED' : 'zh-CN',
  'CHINESE_TRADITIONAL' : 'zh-TW',
  'CROATIAN' : 'hr',
  'CZECH' : 'cs',
  'DANISH' : 'da',
  'DHIVEHI' : 'dv',
  'DUTCH': 'nl',
  'ENGLISH' : 'en',
  'ESPERANTO' : 'eo',
  'ESTONIAN' : 'et',
  'FILIPINO' : 'tl',
  'FINNISH' : 'fi',
  'FRENCH' : 'fr',
  'GALICIAN' : 'gl',
  'GEORGIAN' : 'ka',
  'GERMAN' : 'de',
  'GREEK' : 'el',
  'GUARANI' : 'gn',
  'GUJARATI' : 'gu',
  'HEBREW' : 'iw',
  'HINDI' : 'hi',
  'HUNGARIAN' : 'hu',
  'ICELANDIC' : 'is',
  'INDONESIAN' : 'id',
  'INUKTITUT' : 'iu',
  'ITALIAN' : 'it',
  'JAPANESE' : 'ja',
  'KANNADA' : 'kn',
  'KAZAKH' : 'kk',
  'KHMER' : 'km',
  'KOREAN' : 'ko',
  'KURDISH': 'ku',
  'KYRGYZ': 'ky',
  'LAOTHIAN': 'lo',
  'LATVIAN' : 'lv',
  'LITHUANIAN' : 'lt',
  'MACEDONIAN' : 'mk',
  'MALAY' : 'ms',
  'MALAYALAM' : 'ml',
  'MALTESE' : 'mt',
  'MARATHI' : 'mr',
  'MONGOLIAN' : 'mn',
  'NEPALI' : 'ne',
  'NORWEGIAN' : 'no',
  'ORIYA' : 'or',
  'PASHTO' : 'ps',
  'PERSIAN' : 'fa',
  'POLISH' : 'pl',
  'PORTUGUESE' : 'pt-PT',
  'PUNJABI' : 'pa',
  'ROMANIAN' : 'ro',
  'RUSSIAN' : 'ru',
  'SANSKRIT' : 'sa',
  'SERBIAN' : 'sr',
  'SINDHI' : 'sd',
  'SINHALESE' : 'si',
  'SLOVAK' : 'sk',
  'SLOVENIAN' : 'sl',
  'SPANISH' : 'es',
  'SWAHILI' : 'sw',
  'SWEDISH' : 'sv',
  'TAJIK' : 'tg',
  'TAMIL' : 'ta',
  'TAGALOG' : 'tl',
  'TELUGU' : 'te',
  'THAI' : 'th',
  'TIBETAN' : 'bo',
  'TURKISH' : 'tr',
  'UKRAINIAN' : 'uk',
  'URDU' : 'ur',
  'UZBEK' : 'uz',
  'UIGHUR' : 'ug',
  'VIETNAMESE' : 'vi',
}

_GOOGLE_DETECT_LANGUAGE_BASE_URL = \
        'http://ajax.googleapis.com/ajax/services/language/detect'

_GOOGLE_TRANSLATE_BASE_URL = \
        'http://ajax.googleapis.com/ajax/services/language/translate'
_GOOGLE_CHUNK_SIZE = 500 # Max num of characters that google API accepts

_GOOGLE_TRANSLATE_WEBPAGE_URL = 'http://translate.google.com/translate'

###################
# Language name to google format
###################
class LanguageDoesNotMatchError(Exception):
    pass

def _google_lang(lang):
    ret = lang

    # remove sublang
    if ret.find('-') != -1:
        ret = ret[:ret.find('-')]

    # if it is a key, get the value
    if ret.upper() in _GOOGLE_LANGUAGES.keys():
        ret = _GOOGLE_LANGUAGES[ret.upper()]

    # make sure the language is in _GOOGLE_LANGUAGES.values()
    if ret not in _GOOGLE_LANGUAGES.values():
        raise LanguageDoesNotMatchError, lang

    return ret

###################
# Split into chunks
###################
class ChunkSizeTooSmallError(Exception):
    pass

def _get_chunk_limit(text, splitters, max_size):
    if len(text) <= max_size:
        return len(text)

    for spl in splitters:
        idx = text.rfind(spl, 0, max_size)
        if idx != -1:
            return idx

    raise ChunkSizeTooSmallError, 'the chunk size is too small'

def _gen_chunks(text, splitters, max_size):
    rest = text

    while rest != '':
        idx = _get_chunk_limit(rest, splitters, max_size) + 1
        chunk, rest = rest[:idx], rest[idx:]
        yield chunk

def _get_chunks(text, splitters, max_size):
    # splitters should be ordered by importance (first is the most important)
    return list(_gen_chunks(text, splitters, max_size))

###################
# Caching
###################
class ImmutableDict(dict):
    '''A hashable dict.'''

    def __init__(self, *args, **kwds):
        dict.__init__(self, *args, **kwds)
    def __setitem__(self, key, value):
        raise NotImplementedError, "dict is immutable"
    def __delitem__(self, key):
        raise NotImplementedError, "dict is immutable"
    def clear(self):
        raise NotImplementedError, "dict is immutable"
    def setdefault(self, k, default=None):
        raise NotImplementedError, "dict is immutable"
    def popitem(self):
        raise NotImplementedError, "dict is immutable"
    def update(self, other):
        raise NotImplementedError, "dict is immutable"
    def __hash__(self):
        return hash(tuple(self.iteritems()))

class Memoize:
    def __init__(self, function):
        self._cache = {}
        self._callable = function

    def __call__(self, *args, **kwds):
        cache = self._cache
        key = self._get_key(*args, **kwds)
        try:
            return cache[key]
        except KeyError:
            cached_value = cache[key] = self._callable(*args, **kwds)
            return cached_value

    def _get_key(self, *args, **kwds):
        return kwds and (args, ImmutableDict(kwds)) or args

def cache_method(function):
    return Memoize(function)


###################
# Language detection and translation
###################
class ServiceUnavailableError(Exception):
    pass
class ServiceError(Exception):
    pass

def _detect_lang(text):
    # build url
    params = [('v', '1.0'), ('q', text.encode('utf-8'))]
    url = _GOOGLE_DETECT_LANGUAGE_BASE_URL + '?' + urllib.urlencode(params)

    # call
    page = urllib2.urlopen(url)

    # unpack the data
    result = simplejson.load(page)
    if result is None:
        raise ServiceUnavailableError, 'detection service unavailable'
    elif result['responseStatus'] != 200:
        raise ServiceError, result['responseDetails']
    return result['responseData']['language']

def _translate(text, dest_lang, src_lang):
    # build url
    params = [('v', '1.0'),
            ('langpair', '%s|%s' % (src_lang, dest_lang)),
            ('q', text.encode('utf-8'))]
    url = _GOOGLE_TRANSLATE_BASE_URL + '?' + urllib.urlencode(params)

    # call
    page = urllib2.urlopen(url)

    # unpack the data
    result = simplejson.load(page)
    if result is None:
        raise ServiceUnavailableError, 'translation service unavailable'
    elif result['responseStatus'] != 200:
        raise ServiceError, result['responseDetails']
    return result['responseData']['translatedText']

###################
# Interface
###################
@cache_method
def translate(text, dest_lang, src_lang=None):
    try:
        # split into chunks
        chunks = _get_chunks(text, '.!?, ', _GOOGLE_CHUNK_SIZE)

        # match the destination language for the call
        dest_lang = _google_lang(dest_lang)

        # match the source language for the call
        if src_lang is None:
            src_lang = _detect_lang(chunks[0])
        else:
            try:
                src_lang = _google_lang(src_lang)
            except LanguageDoesNotMatchError:
                # if wrong src_lang try to detect it
                src_lang = _detect_lang(chunks[0])

        # translate every chunk
        ret = ''
        for chunk in chunks:
            ret += _translate(chunk, dest_lang, src_lang)
        return ret
    except (ChunkSizeTooSmallError, LanguageDoesNotMatchError,
            ServiceUnavailableError, ServiceError):
        # on error return the original text
        return text

def translate_url(url, dest_lang, src_lang):
    url = url.encode('utf-8')
    params = [('hl', dest_lang),
            ('sl', src_lang),
            ('tl', dest_lang),
            ('u', url)]
    url = _GOOGLE_TRANSLATE_WEBPAGE_URL + '?' + urllib.urlencode(params)
    return url


###################
# Unit tests
###################
import unittest

class TestTranslation(unittest.TestCase):
    def test__google_lang(self):
        self.assertEqual(_google_lang('English'), 'en')
        self.assertEqual(_google_lang('en-us'), 'en')
        self.assertRaises(LanguageDoesNotMatchError, _google_lang, 'cal')

    def test__detect_lang(self):
        self.assertEqual(_detect_lang('Ciao mondo'), 'it')
        self.assertEqual(_detect_lang('Hello world'), 'en')
        self.assertEqual(_detect_lang('Buna ziua'), 'ro')

    def test__translate(self):
        self.assertEqual(_translate('Ciao mondo', 'en', 'it'),
                'Hello world')
        self.assertEqual(_translate('Buna ziua lume', 'en', 'ro'),
                'Hello world')

    def test_translate(self):
        self.assertEqual(translate('Ciao mondo', 'en'), 'Hello world')
        self.assertEqual(translate('Buna ziua lume', 'en'), 'Hello world')
        translate(u'Frauen sind anders, M\xc3\xa4nner auch \xc2\x96 ein'
                u' Thema f\xc3\xbcr die Umweltpolitik?', 'en')

class TestTranslateURL(unittest.TestCase):
    def test_translate_url(self):
        self.assertEqual(translate_url('http://google.com', 'it', 'en'),
            'http://translate.google.com/translate'
            '?hl=it&sl=en&tl=it&u=http%3A%2F%2Fgoogle.com')

if __name__ == '__main__':
    unittest.main()
