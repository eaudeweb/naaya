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

_GOOGLE_URL = "http://ajax.googleapis.com/ajax/services/language/translate?v=1.0"
_GOOGLE_TRANSLATE_URL = "http://translate.google.com/translate?hl=en"
_GOOGLE_CHUNK_SIZE = 500 # Max num of characters that google API accepts

class ChunkSizeTooSmallError(Exception):
    pass

def get_max_chunk_idx(text, splitters, max_size):
    if len(text) <= max_size:
        return len(text)

    max_idx = -1

    for sp in splitters:
        idx = text.rfind(sp, 0, max_size)
        if max_idx < idx:
            max_idx = idx

    if max_idx == -1:
        raise ChunkSizeTooSmallError, 'the chunk size is too small'

    return max_idx

def gen_chunks(text, splitters, max_size):
    s = text

    idx = get_max_chunk_idx(s, splitters, max_size) + 1
    while len(s) > idx:
        yield s[:idx]

        s = s[idx:]
        idx = get_max_chunk_idx(s, splitters, max_size) + 1
    yield s

class ServiceUnavailableError(Exception):
    pass
class ServiceError(Exception):
    pass

def _translate(text, src_lang, dest_lang):
    vars = [('langpair', '%s|%s' % (src_lang, dest_lang)), ('q', text)]
    url = _GOOGLE_URL + '&' + urllib.urlencode(vars)
    t = urllib2.urlopen(url)
    d = simplejson.load(t)
    if d == None:
        raise ServiceUnavailableError, 'translation service unavailable'
    elif d['responseStatus'] != 200:
        raise ServiceError, d['responseDetails']
    return d['responseData']['translatedText']

class Memoize:
    def __init__(self,function):
        self._cache = {}
        self._callable = function

    def __call__(self, *args, **kwds):
        cache = self._cache
        key = self._getKey(*args,**kwds)
        try: return cache[key]
        except KeyError:
            cachedValue = cache[key] = self._callable(*args,**kwds)
            return cachedValue

    def _getKey(self,*args,**kwds):
        return kwds and (args, ImmutableDict(kwds)) or args

def cache_method(function):
    return Memoize(function)

def remove_sublang(lang):
    if lang.find('-') != -1:
        return lang[:lang.find('-')]
    return lang

@cache_method
def translate(text, src_lang, dest_lang):
    text = text.encode('utf-8')
    src_lang = remove_sublang(src_lang)
    dest_lang = remove_sublang(dest_lang)

    # make sure the languages are in the _GOOGLE_LANGUAGE.values()
    if src_lang not in _GOOGLE_LANGUAGES.values():
        if src_lang.upper() in _GOOGLE_LANGUAGES.keys():
            src_lang = _GOOGLE_LANGUAGES[src_lang.upper()]
        else:
            return text

    if dest_lang not in _GOOGLE_LANGUAGES.values():
        if dest_lang.upper() in _GOOGLE_LANGUAGES.keys():
            dest_lang = _GOOGLE_LANGUAGES[dest_lang.upper()]
        else:
            return text

    if src_lang == dest_lang:
        return text

    try:
        translated_text = ''
        for chunk in gen_chunks(text, ' ,.', _GOOGLE_CHUNK_SIZE):
            translated_text += _translate(chunk, src_lang, dest_lang)
        return translated_text
    except Exception, e:
        # on error return the original text
        return text

def translation_url(url, src_lang, dest_lang):
    url = url.encode('utf-8')
    vars = [('sl', src_lang), ('tl', dest_lang), ('u', url)]
    url = _GOOGLE_TRANSLATE_URL + '&' + urllib.urlencode(vars)
    return url

