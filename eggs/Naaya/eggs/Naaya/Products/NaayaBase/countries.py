
# from http://www.nationsonline.org/oneworld/european_languages.htm
_COUNTRY_TO_LANGUAGE = {
        'Albania': 'Albanian',
        'Andorra': 'Catalan',
        'Austria': 'German',
        'Belarus': 'Belarusian',
        'Belgium': 'Dutch',
        'Bosnia and herzegovina': ['Bosnian', 'Croatian', 'Serbian'],
        'Bulgaria': 'Bulgarian',
        'Croatia': 'Croatian',
        'Cyprus': 'Greek',
        'Czech republic': 'Czech',
        'Denmark': 'Danish',
        'Estonia': 'Estonian',
        'Faroe islands': ['Faroese', 'Danish'],
        'Finland': 'Finnish',
        'France': 'French',
        'Germany': 'German',
        'Gibraltar': 'English',
        'Greece':  'Greek',
        'Greenland': ['Greenlandic', 'Danish'],
        'Hungary': 'Hungarian',
        'Iceland': 'Icelandic',
        'Ireland': 'Irish',
        'Italy': 'Italian',
        'Latvia': 'Latvian',
        'Liechtenstein': 'German',
        'Lithuania': 'Lithuanian',
        'Luxembourg': ['Luxembourgish', 'French', 'German'],
        'Macedonia': ['Macedonian', 'Albanian'],
        'Malta': 'Maltese',
        'Moldova': ['Moldovan', 'Romanian'],
        'Monaco': 'French',
        'Montenegro': 'Serbian',
        'Netherlands': 'Dutch',
        'Norway': 'Norwegian',
        'Poland': 'Polish',
        'Portugal': 'Portuguese',
        'Romania': 'Romanian',
        'Russian federation': 'Russian',
        'San marino': 'Italian',
        'Serbia': 'Serbian',
        'Slovakia': 'Slovak',
        'Slovenia': 'Slovenian',
        'Spain': ['Spanish', 'Catalan'],
        'Sweden': 'Swedish',
        'Switzerland': ['German', 'French', 'Italian'],
        'Turkey': 'Turkish',
        'Ukraine': 'Ukrainian',
        'United kingdom': 'English',
        'Vatican city': ['Latin', 'Italian'],
    }

# from http://www.iso.org/iso/list-en1-semic-3.txt
_COUNTRY_CODE_TO_COUNTRY = {
        'AL': 'ALBANIA',
        'AD': 'ANDORRA',
        'AT': 'AUSTRIA',
        'BY': 'BELARUS',
        'BE': 'BELGIUM',
        'BA': 'BOSNIA AND HERZEGOVINA',
        'BG': 'BULGARIA',
        'HR': 'CROATIA',
        'CY': 'CYPRUS',
        'CZ': 'CZECH REPUBLIC',
        'DK': 'DENMARK',
        'EE': 'ESTONIA',
        'FO': 'FAROE ISLANDS',
        'FI': 'FINLAND',
        'FR': 'FRANCE',
        'DE': 'GERMANY',
        'GI': 'GIBRALTAR',
        'GR': 'GREECE',
        'GL': 'GREENLAND',
        'HU': 'HUNGARY',
        'IS': 'ICELAND',
        'IE': 'IRELAND',
        'IT': 'ITALY',
        'LV': 'LATVIA',
        'LI': 'LIECHTENSTEIN',
        'LT': 'LITHUANIA',
        'LU': 'LUXEMBOURG',
        'MK': 'MACEDONIA',
        'MT': 'MALTA',
        'MD': 'MOLDOVA',
        'MC': 'MONACO',
        'ME': 'MONTENEGRO',
        'NL': 'NETHERLANDS',
        'NO': 'NORWAY',
        'PL': 'POLAND',
        'PT': 'PORTUGAL',
        'RO': 'ROMANIA',
        'RU': 'RUSSIAN FEDERATION',
        'SM': 'SAN MARINO',
        'RS': 'SERBIA',
        'SK': 'SLOVAKIA',
        'SI': 'SLOVENIA',
        'ES': 'SPAIN',
        'SE': 'SWEDEN',
        'CH': 'SWITZERLAND',
        'TR': 'TURKEY',
        'UA': 'UKRAINE',
        'GB': 'UNITED KINGDOM',
        'VA': 'VATICAN CITY',
    }

# from http://www.iana.org/assignments/language-subtag-registry
_LANGUAGE_TO_LANGUAGE_CODE = {
        'Albanian': 'sq',
        'Belarusian': 'be',
        'Bosnian': 'bs',
        'Bulgarian': 'bg',
        'Catalan': 'ca',
        'Croatian': 'hr',
        'Czech': 'cs',
        'Danish': 'da',
        'Dutch': 'nl',
        'Estonian': 'et',
        'English': 'en',
        'Faroese': 'fo',
        'Finnish': 'fi',
        'French': 'fr',
        'German': 'de',
        'Greek': 'el',
        'Greenlandic': 'kl',
        'Hungarian': 'hu',
        'Icelandic': 'is',
        'Irish': 'ga',
        'Italian': 'it',
        'Latin': 'la',
        'Latvian': 'lv',
        'Lithuanian': 'lt',
        'Luxembourgish': 'lb',
        'Macedonian': 'mk',
        'Maltese': 'mt',
        'Moldovan': 'mo',
        'Norwegian': 'no',
        'Polish': 'pl',
        'Portuguese': 'pt',
        'Romanian': 'ro',
        'Russian': 'ru',
        'Serbian': 'sr',
        'Slovak': 'sk',
        'Slovenian': 'sl',
        'Spanish': 'es',
        'Swedish': 'sv',
        'Turkish': 'tr',
        'Ukrainian': 'uk',
    }

def language_from_country_code(country_code):
    country = _COUNTRY_CODE_TO_COUNTRY[country_code.upper()]
    language = _COUNTRY_TO_LANGUAGE[country.capitalize()]

    if isinstance(language, list):
        language = language[0]

    return language

def language_code_from_country_code(country_code):
    language = language_from_country_code(country_code)
    language_code = _LANGUAGE_TO_LANGUAGE_CODE[language.capitalize()]
    return language_code

###################
# Unit tests
###################
import unittest

class TestCountryToLanguage(unittest.TestCase):
    def test_language_from_country_code(self):
        self.assertEqual(language_from_country_code('gb'), 'English')
        self.assertEqual(language_from_country_code('es'), 'Spanish')
        self.assertEqual(language_from_country_code('cz'), 'Czech')
        self.assertEqual(language_from_country_code('ru'), 'Russian')
        self.assertEqual(language_from_country_code('ba'), 'Bosnian')
        self.assertEqual(language_from_country_code('ua'), 'Ukrainian')
        self.assertEqual(language_from_country_code('va'), 'Latin')
        self.assertEqual(language_from_country_code('ro'), 'Romanian')
        self.assertEqual(language_from_country_code('ee'), 'Estonian')

        self.assertRaises(KeyError, language_from_country_code, 'com')

    def test_language_code_from_country_code(self):
        self.assertEqual(language_code_from_country_code('gb'), 'en')
        self.assertEqual(language_code_from_country_code('es'), 'es')
        self.assertEqual(language_code_from_country_code('cz'), 'cs')
        self.assertEqual(language_code_from_country_code('ru'), 'ru')
        self.assertEqual(language_code_from_country_code('ba'), 'bs')
        self.assertEqual(language_code_from_country_code('ua'), 'uk')
        self.assertEqual(language_code_from_country_code('va'), 'la')
        self.assertEqual(language_code_from_country_code('ro'), 'ro')
        self.assertEqual(language_code_from_country_code('ee'), 'et')

        self.assertRaises(KeyError, language_code_from_country_code, 'com')

if __name__ == '__main__':
    unittest.main()

