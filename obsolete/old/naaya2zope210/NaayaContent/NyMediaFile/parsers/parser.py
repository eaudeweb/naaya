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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
# Alin Voinea, Eau de Web
""" Abstract parser module
"""
class Parser:
    """ Abstract parser class to subclass
    """
    def __init__(self, text=""):
        self.text = text
        
    def parse(self):
        """ Return unparsed text. Override this in your subclass in order to 
        parse text.
        """
        return self.text