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
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
import HTMLParser
import re

#Zope imports

#Product imports

class stripping_tool(HTMLParser.HTMLParser):
    """ """

    from htmlentitydefs import entitydefs

    def __init__(self, valid_tags, tolerate_missing_closing_tags):
        """ """
        self.valid_tags = valid_tags
        self.tolerate_missing_closing_tags = tolerate_missing_closing_tags
        HTMLParser.HTMLParser.__init__(self)
        HTMLParser.attrfind = re.compile(r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~@]*))?')
        self.result = []
        self.endTagList = []

    def handle_data(self, data):
        """ """
        self.result.append(data)

    def handle_charref(self, name):
        """ """
        self.result.append("&#%s;" % name)

    def handle_entityref(self, name):
        """ """
        x= ';' * self.entitydefs.has_key(name)
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
