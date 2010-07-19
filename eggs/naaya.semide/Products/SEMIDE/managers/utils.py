# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Finsiel Romania

#Python imports
import locale
import operator
import re
from htmlentitydefs import entitydefs
import HTMLParser
import string


def utConvertToListExact(data):
    """Convert to list"""
    ret = data
    if not isinstance(data, list):
        if data: ret = [data]
        else:    ret = []
    return ret

def utSortObjsByLocaleAttr(p_list, p_attr, p_desc=1, p_locale=''):
    """Sort a list of objects by an attribute values based on locale"""
    if not p_locale:
        #normal sorting
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc: l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)
    else:
        #locale sorting based
        try:
            default_locale = locale.setlocale(locale.LC_ALL)

            try:
                #try to set for NT, WIN operating systems
                locale.setlocale(locale.LC_ALL, p_locale)
            except:
                #try to set for other operating system
                if p_locale == 'ar': p_locale = 'ar_DZ'
                else:                p_locale = '%s_%s' % (p_locale, p_locale.upper())
                locale.setlocale(locale.LC_ALL, p_locale)

            #sorting
            l_len = len(p_list)
            l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
            l_temp.sort(lambda x, y: locale.strcoll(x[0], y[0]))
            if p_desc: l_temp.reverse()

            locale.setlocale(locale.LC_ALL, default_locale)
            return map(operator.getitem, l_temp, (-1,)*l_len)
        except:
            #in case of failure make a normal sorting
            locale.setlocale(locale.LC_ALL, default_locale)
            return utSortObjsByLocaleAttr(p_list, p_attr, p_desc)

class html_utils(HTMLParser.HTMLParser):
    """ """

    def __init__(self):
        """ """
        HTMLParser.HTMLParser.__init__(self)
        self.result = []
        self.endTagList = []
        self.set_valid_tags(())
        self.set_tolerate_missing_closing_tags(())

        self.start_tag_marker = "\0\1\0"
        self.end_tag_marker = "\0\2\0"

    def set_valid_tags (self, valid_tags):
        self.valid_tags = valid_tags

    def set_tolerate_missing_closing_tags(self, tolerate_missing_closing_tags):
        self.tolerate_missing_closing_tags = tolerate_missing_closing_tags

    def handle_data(self, data):
        """ """
        self.result.append(data)

    def handle_charref(self, name):
        """ """
        self.result.append("&#%s;" % name)

    def handle_entityref(self, name):
        """ """
        x= ';' * entitydefs.has_key(name)
        self.result.append("&%s%s" % (name, x))

    def handle_starttag(self, tag, attrs):
        """ """
        if tag in self.valid_tags:
            self.result.append('<' + tag)
            for k,v in attrs:
                if k[0:2].lower() != 'on' and v[0:10].lower() != 'javascript':
                    self.result.append(' %s="%s"' % (k, v))
            endTag = '</%s>' % tag
            self.endTagList.insert(0, endTag)
            self.result.append('>')

    def handle_endtag(self, tag):
        """ """
        if tag in self.valid_tags:
            endTag = '</%s>' % tag
            self.result.append(endTag)
            try:
                self.endTagList.remove(endTag)
            except:
                pass

    def cleanup(self):
        """ """
        self.result.extend(self.endTagList)

    def stripAllHtmlTags(self, p_html_string):
        """Removes all html tags from an html string"""
        try:
            l_parser = html_utils()
            l_parser.feed(p_html_string)
            l_parser.close()
            l_parser.cleanup()
        except Exception, err:
            # XXX Handle err
            return p_html_string
        else:
            return ' '.join([x.strip() for x in l_parser.result]).replace('&nbsp', ' ')

    def stripHtmlTags(self, p_html_string):
        """removes the html tags that are not allowe from a string"""
        l_parser = StrippingParser(self.get_htmltags_all_tags(), self.get_htmltags_single_tags())
        try:
            l_parser.feed(p_html_string)
            l_parser.close()
        except:
            l_result = []
        else:
            l_result = l_parser.result
        l_parser.cleanup()
        return ' '.join(l_result)

    def splitTextToSentences(self, p_text):
        """Splits a text into sentences"""
        l_delimiters = ".!?;,"
        for delimiter in l_delimiters:
            p_text = p_text.replace(delimiter, ".")
        return [x for x in p_text.split(".") if x.strip()!=""]


    def highlightWordsInHtml(self, p_text, p_words="", p_highlight_start="<span class='hlighted'>", p_highlight_end="</span>", p_phrases = 3, p_nosplit=False):
        """Same as highlightWordsInText, but also strips the HTML tags"""
        return self.highlightWordsInText(self.stripAllHtmlTags(p_text), p_words, p_highlight_start, p_highlight_end, p_phrases, p_nosplit)

    def highlightWordsInText(self, p_text, p_words="", p_highlight_start="<span class='hlighted'>", p_highlight_end="</span>", p_phrases = 3, p_nosplit=False):
        """Highlights the list of words in p_text, and returns only the most relevant sentences."""
        p_words = [x for x in p_words.split() if x.lower() not in ['', 'or', 'and', 'not']]
        l_sentences = p_text
        #extract the important sentences only if p_text excides 160 chars
        if len(l_sentences) > 160 and p_nosplit==False:
            l_sentences = self.splitTextToSentences(l_sentences)
        else:
            l_sentences = [l_sentences]
        #lists_format is: (number of occurences, sentence, index of sentence)
        l_data = [ [0, l_sentences[x].strip(), x] for x in range(0, len(l_sentences))]
        #set the occurence no. for each sentence
        for i in range(0, len(l_data)):
            l_occurences = 0
            for word in p_words:
                if self.reReplace(word, l_data[i][1], 1):
                    l_occurences += 1
            l_data[i][0] = l_occurences
        #extract only the most relevant sentences (with most occurances), and keep them in the original order
        l_data.sort()
        l_data.reverse()
        l_data = [x for x in l_data[:p_phrases]]
        l_data = [[l_data[x][2], l_data[x][1], l_data[x][0]] for x in range(0, len(l_data)) ]
        l_data.sort()
        l_data = [x[1] for x in l_data]
        for y in p_words:
            l_data = [self.reReplace(y, x) for x in l_data]
        l_data = [x.replace(self.start_tag_marker, p_highlight_start).replace(self.end_tag_marker, p_highlight_end) for x in l_data]
        return " [...] ".join(l_data)

    def reReplace(self, p_query, p_text, p_info=0):
        """encloses p_query in tags within p_text"""
        #decide if * search syntax was used
        p_query = self.utToUtf8(p_query)
        word_begin = p_query[-1] == '*'
        p_query = p_query.translate(string.maketrans('*.,()[]{}|?#<>=!\\', '                 '))

        p_query = self.utToUnicode(p_query)
        p_text = self.utToUnicode(p_text)

        #cleanup characters for regexp use
        p_query = p_query.replace(' ', '')

        if word_begin:
            p = re.compile('\\b'+p_query+'\\w*', re.UNICODE | re.IGNORECASE)
        else:
            p = re.compile('\\b'+p_query+'\\b', re.UNICODE | re.IGNORECASE)
        if p_info:
            return p.search(p_text)
        else:
            return p.sub(self.reReplaceFunction, p_text)

    def reReplaceFunction(self, match):
        """function for reReplace function"""
        return self.start_tag_marker + match.group() + self.end_tag_marker

    def utToUtf8(self, p_string):
        #convert to utf-8
        if isinstance(p_string, unicode): return p_string.encode('utf-8')
        else: return str(p_string)

    def utToUnicode(self, p_string):
        #convert to unicode
        if not isinstance(p_string, unicode): return unicode(p_string, 'utf-8')
        else: return p_string