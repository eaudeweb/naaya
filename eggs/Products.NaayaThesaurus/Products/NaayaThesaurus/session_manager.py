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
# Ghica Alexandru, Finsiel Romania

# product imports
from Products.NaayaCore.managers.session_manager import session_manager

class session_manager(session_manager):
    """This class has some methods to work with session variables"""

    def __init__(self):
        """Constructor"""
        pass


    #concept_id
    def isSessionConceptId(self):
        return self.__isSession('concept_id')

    def setSessionConceptId(self, concept_id):
        self.__setSession('concept_id', concept_id)

    def getSessionConceptId(self, default=None):
        return self.__getSession('concept_id', default)

    def delSessionConceptId(self):
        self.__delSession('concept_id')


    #theme_id
    def isSessionThemeId(self):
        return self.__isSession('theme_id')

    def setSessionThemeId(self, theme_id):
        self.__setSession('theme_id', theme_id)

    def getSessionThemeId(self, default=None):
        return self.__getSession('theme_id', default)

    def delSessionThemeId(self):
        self.__delSession('theme_id')


    #theme_name
    def setSessionThemeName(self, theme_name):
        self.__setSession('theme_name', theme_name)

    def getSessionThemeName(self, default=None):
        return self.__getSession('theme_name', default)

    def delSessionThemeName(self):
        self.__delSession('theme_name')


    #langcode
    def setSessionLangcode(self, langcode):
        self.__setSession('langcode', langcode)

    def getSessionLangcode(self, default=None):
        return self.__getSession('langcode', default)

    def delSessionLangcode(self):
        self.__delSession('langcode')


    #relation_id
    def setSessionRelationId(self, relation_id):
        self.__setSession('relation_id', relation_id)

    def getSessionRelationId(self, default=None):
        return self.__getSession('relation_id', default)

    def delSessionRelationId(self):
        self.__delSession('relation_id')


    #relation_type
    def setSessionRelationType(self, relation_type):
        self.__setSession('relation_type', relation_type)

    def getSessionRelationType(self, default=None):
        return self.__getSession('relation_type', default)

    def delSessionRelationType(self):
        self.__delSession('relation_type')


    #concept_name
    def setSessionConceptName(self, concept_name):
        self.__setSession('concept_name', concept_name)

    def getSessionConceptName(self, default=None):
        return self.__getSession('concept_name', default)

    def delSessionConceptName(self):
        self.__delSession('concept_name')


    #source_id
    def setSessionSourceId(self, source_id):
        self.__setSession('source_id', source_id)

    def getSessionSourceId(self, default=None):
        return self.__getSession('source_id', default)

    def delSessionSourceId(self):
        self.__delSession('source_id')


    #definition
    def setSessionDefinition(self, definition):
        self.__setSession('definition', definition)

    def getSessionDefinition(self, default=None):
        return self.__getSession('definition', default)

    def delSessionDefinition(self):
        self.__delSession('definition')


    #alt_name
    def setSessionAltName(self, alt_name):
        self.__setSession('alt_name', alt_name)

    def getSessionAltName(self, default=None):
        return self.__getSession('alt_name', default)

    def delSessionAltName(self):
        self.__delSession('alt_name')


    #scope_note
    def setSessionScopeNote(self, scope_note):
        self.__setSession('scope_note', scope_note)

    def getSessionScopeNote(self, default=None):
        return self.__getSession('scope_note', default)

    def delSessionScopeNote(self):
        self.__delSession('scope_note')
