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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Valentin Dumitru, Eau de Web


#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript 

class UpdateLandscapeType(UpdateScript):
    """ Update script  """
    title = 'Destinet: Update landscape_type and administrative_level from missing or "" to "Unspecified" + other corrections'
    creation_date = 'Feb 23, 2012'
    authors = ['Valentin Dumitru']
    description = 'Destinet: Update landscape_type and administrative_level from missing or "" to "Unspecified" + other corrections'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        administrative_replacements = {
                'Unspecified': ['', 'unspecified', [u'unspecified'],
                    u"[u'unspecified']"],
                'Local': ['local'],
                'Sub-Global': ['Sub-global', 'sub-global', 'Sub-Golbal'],
                'Regional': ['regional'],
                'National': ['national', 'National, Regional']
                }
        landscape_replacements = {
                'all': [[u"[u'Urban'", u"u'Forest'", u"u'Coastal'", u"u'Marine'", u"u'Mountain'", u"u'Protected'", u"u'Rural']"],
                    [u'Urban', u'Forest', u'Coastal', u'Marine', u'Mountains', u'Protected', u'Rural']],
                'Coastal': [[u"[u'Coastal']"], [u"[u'coastal']"],
                    [u'[u"[u\'Coastal\']"]'],
                    [u'C', u'o', u'a', u's', u't', u'a', u'l']],
                'coastal-marine': [[u"[u'Coastal'", u"u'Marine']"]],
                'coastal-mountain-protected': [[u"[u'Coastal'", u"u'Mountain'", u"u'Protected']"]],
                'Forest': [[u"[u'Forest']"],
                    [u'[', u'u', u"'", u'F', u"'", u',', u' ', u'u', u"'", u'o', u"'", u',', u' ', u'u', u"'", u'r', u"'", u',', u' ', u'u', u"'", u'e', u"'", u',', u' ', u'u', u"'", u's', u"'", u',', u' ', u'u', u"'", u't', u"'", u']']],
                'forest-mountain-protected-rural': [[u"[u'Forest'", u"u'Mountain'", u"u'Protected'", u"u'Rural']"]],
                'forest-mountain-rural': [[u"[u'Forest'", u"u'Mountain'", u"u'Rural']"]],
                'Marine': [[u"[u'Marine']"], [u"[u'marine']"]],
                'Mountain': [[u"[u'M'", u"u'o'", u"u'u'", u"u'n'", u"u't'", u"u'a'", u"u'i'", u"u'n']"],
                    [u"[u'Mountain']"], [u'[u"[u\'Mountain\']"]'],
                    [u'M', u'o', u'u', u'n', u't', u'a', u'i', u'n'],
                    [u'[', u'u', u"'", u'M', u"'", u',', u' ', u'u', u"'", u'o', u"'", u',', u' ', u'u', u"'", u'u', u"'", u',', u' ', u'u', u"'", u'n', u"'", u',', u' ', u'u', u"'", u't', u"'", u',', u' ', u'u', u"'", u'a', u"'", u',', u' ', u'u', u"'", u'i', u"'", u',', u' ', u'u', u"'", u'n', u"'", u']']],
                'mountain-rural': [[u"[u'Mountain'", u"u'Rural']"]],
                'Protected': [[u"[u'Protected']"],
                    [u'[', u'u', u"'", u'P', u'r', u'o', u't', u'e', u'c', u't', u'e', u'd', u"'", u']']],
                'protected-rural': [[u"[u'Protected'", u"u'Rural']"]],
                'Rural': [[u"[u'R'", u"u'u'", u"u'r'", u"u'a'", u"u'l']"],
                    [u"[u'['", u"u'u'", u'u"\'"', u"u'R'", u"u'u'", u"u'r'", u"u'a'", u"u'l'", u'u"\'"', u"u']']"],
                    [u"[u'Rural']"], [u"[u'rural']"], [u'[u"[u\'Rural\']"]'],
                    [u'[', u'u', u"'", u'R', u'u', u'r', u'a', u'l', u"'", u']'],
                    [u'R', u'u', u'r', u'a', u'l'],
                    [u'[', u'u', u"'", u'R', u"'", u',', u' ', u'u', u"'", u'u', u"'", u',', u' ', u'u', u"'", u'r', u"'", u',', u' ', u'u', u"'", u'a', u"'", u',', u' ', u'u', u"'", u'l', u"'", u']']],
                'Unspecified': [[u"[u'U'", u"u'n'", u"u's'", u"u'p'", u"u'e'", u"u'c'", u"u'i'", u"u'f'", u"u'i'", u"u'e'", u"u'd']"],
                    [u"[u'Unspecified']"], [u"['Unspecified']"],
                    [u"[u'['", u"u'u'", u'u"\'"', u"u'U'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'n'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u's'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'p'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'e'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'c'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'i'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'f'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'i'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'e'", u'u"\'"', u"u'", u"'", u"u' '", u"u'u'", u'u"\'"', u"u'd'", u'u"\'"', u"u']']"],
                    [u"[u'['", u"u'u'", u'u"\'"', u"u'U'", u"u'n'", u"u's'", u"u'p'", u"u'e'", u"u'c'", u"u'i'", u"u'f'", u"u'i'", u"u'e'", u"u'd'", u'u"\'"', u"u']']"],
                    [u"[u'unspecified']"], [u'unspecified'],
                    [u'U', u'n', u's', u'p', u'e', u'c', u'i', u'f', u'i', u'e', u'd'],
                    [u'[', u'u', u"'", u'U', u"'", u',', u' ', u'u', u"'", u'n', u"'", u',', u' ', u'u', u"'", u's', u"'", u',', u' ', u'u', u"'", u'p', u"'", u',', u' ', u'u', u"'", u'e', u"'", u',', u' ', u'u', u"'", u'c', u"'", u',', u' ', u'u', u"'", u'i', u"'", u',', u' ', u'u', u"'", u'f', u"'", u',', u' ', u'u', u"'", u'i', u"'", u',', u' ', u'u', u"'", u'e', u"'", u',', u' ', u'u', u"'", u'd', u"'", u']'],
                    [u'U', u'n', u's', u'p', u'e', u'c', u'i', u'f', u'i', u'e', u'd'],
                    [u'[', u'u', u"'", u'U', u'n', u's', u'p', u'e', u'c', u'i', u'f', u'i', u'e', u'd', u"'", u']'],
                    [u'[', u"'", u'U', u"'", u',', u' ', u"'", u'n', u"'", u',', u' ', u"'", u's', u"'", u',', u' ', u"'", u'p', u"'", u',', u' ', u"'", u'e', u"'", u',', u' ', u"'", u'c', u"'", u',', u' ', u"'", u'i', u"'", u',', u' ', u"'", u'f', u"'", u',', u' ', u"'", u'i', u"'", u',', u' ', u"'", u'e', u"'", u',', u' ', u"'", u'd', u"'", u']']],
                'Urban': [[u'[', u'u', u"'", u'U', u"'", u',', u' ', u'u', u"'", u'r', u"'", u',', u' ', u'u', u"'", u'b', u"'", u',', u' ', u'u', u"'", u'a', u"'", u',', u' ', u'u', u"'", u'n', u"'", u']'],
                    [u"[u'Urban']"], [u"[u'Urban'", u"u'Unspecified']"],
                    [u"[u'urban']"], [u'U', u'r', u'b', u'a', u'n']],
                'urban-protected-rural': [[u"[u'Urban'", u"u'Protected'", u"u'Rural']"]],
                }
        landscape_types = ['Urban', 'Forest', 'Coastal', 'Marine', 'Mountain',
                'Protected', 'Rural', 'Unspecified']
        administrative_levels = ['Local', 'Regional', 'National', 'Sub-Global',
                'Global', 'Unspecified']
        schema_tool = portal.getSchemaTool()
        schemas = schema_tool.listSchemas().items()
        for meta_type, schema in schemas:
            no_landscape = False
            landscape_localized = False
            no_administrative_level = False
            administrative_level_localized = False
            if not getattr(schema, 'landscape_type-property', None):
                no_landscape = True
            else:
                landscape_localized = getattr(schema,
                        'landscape_type-property').localized
            if not getattr(schema, 'administrative_level-property', None):
                no_administrative_level = True
            else:
                administrative_level_localized = getattr(schema,
                        'administrative_level-property').localized

            for ob in portal.getCatalogedObjects(meta_type=meta_type):
                changed = False

                if no_landscape:
                    if ob.hasLocalProperty('landscape_type'):
                        ob.del_localproperty('landscape_type')
                        changed = True
                        self.log.debug('Landscape type (local property) deleted from %s' %
                            ob.absolute_url())
                    if hasattr(ob.aq_base, 'landscape_type'):
                        del ob.landscape_type
                        changed = True
                        self.log.debug('Landscape type deleted from %s' %
                            ob.absolute_url())
                else:
                    if not hasattr(ob.aq_base, 'landscape_type') or ob.landscape_type == '':
                        ob.set_localpropvalue('landscape_type', 'en', ['Unspecified'])
                        self.log.debug('Landscape type set to ["Unspecified"] for %s' %
                            ob.absolute_url())
                        changed = True
                    if isinstance(ob.landscape_type, basestring):
                        if landscape_localized:
                            if ob.landscape_type == 'protected':
                                ob.set_localpropvalue('landscape_type', 'en', ['Protected'])
                                try:
                                    del ob.landscape_type
                                except AttributeError:
                                    pass
                                self.log.debug(
                                        'Landscape type moved from "protected" to '
                                        'local property ["Protected"] for %s' %
                                    ob.absolute_url())
                            else:
                                if ob.landscape_type in landscape_types:
                                    ob.set_localpropvalue('landscape_type', 'en', [ob.landscape_type])
                                    try:
                                        del ob.landscape_type
                                    except AttributeError:
                                        pass
                                    self.log.debug(
                                        'Landscape type moved to local property %s for %s' %
                                        (ob.landscape_type, ob.absolute_url()))
                                else:
                                     self.log.error('Unhandled landscape type value %s'
                                             % ob.landscape_type)
                        else:
                            if ob.landscape_type == 'protected':
                                ob.landscape_type = ['Protected']
                                self.log.debug(
                                    'Landscape type set to ["Protected"] for %s' %
                                    ob.absolute_url())
                            else:
                                if ob.landscape_type in landscape_types:
                                    ob.landscape_type = [ob.landscape_type]
                                    self.log.debug(
                                        'Landscape type set to %s for %s' %
                                        (ob.landscape_type, ob.absolute_url()))
                                else:
                                     self.log.error('Unhandled landscape type value '
                                                    '%s for object %s'
                                             % (ob.landscape_type, ob.absolute_url()))
                        changed = True
                    for key, values in landscape_replacements.items():
                        if ob.landscape_type in values:
                            if landscape_localized:
                                if key == 'all':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Urban', 'Forest', 'Coastal', 'Marine',
                                             'Mountain','Protected', 'Rural'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Urban", "Forest", '
                                            '"Coastal", "Marine", "Mountain", '
                                            '"Protected", "Rural"] for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'coastal-marine':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Coastal', 'Marine'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Coastal", "Marine"] '
                                            'for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'coastal-mountain-protected':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Coastal', 'Mountain','Protected'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Coastal", "Mountain", '
                                            '"Protected"] for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'forest-mountain-protected-rural':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Forest', 'Mountain', 'Protected', 'Rural'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Forest", "Mountain", '
                                            '"Protected", "Rural"] for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'forest-mountain-rural':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Forest', 'Mountain','Rural'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Forest", "Mountain", '
                                            '"Rural"] for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'mountain-rural':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Mountain','Rural'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Mountain", "Rural"] '
                                            'for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'protected-rural':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Protected','Rural'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Protected", "Rural"] '
                                            'for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                elif key == 'urban-protected-rural':
                                    ob.set_localpropvalue('landscape_type', 'en',
                                         ['Urban', 'Protected', 'Rural'])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized ["Urban", "Protected", '
                                            '"Rural"] for object %s'
                                            % (ob.landscape_type, ob.absolute_url()))
                                else:
                                    ob.set_localpropvalue('landscape_type', 'en',
                                            [key])
                                    self.log.debug('Landscape type corrected from %s '
                                            'to localized [%s] for object %s'
                                            % (ob.landscape_type, key,
                                                ob.absolute_url()))
                                try:
                                    del ob.landscape_type
                                except AttributeError:
                                    pass
                            else:
                                ob.landscape_type = [key]
                                self.log.debug('Landscape type corrected from a '
                                        'fantastic list to [%s] for object %s'
                                        % (key, ob.absolute_url()))
                            changed = True

                    for item in ob.landscape_type:
                        if item not in landscape_types:
                            self.log.error('Unhandled landscape type value %s for object %s'
                                    % (ob.landscape_type, ob.absolute_url()))


                if no_administrative_level:
                    if hasattr(ob.aq_base, 'administrative_level'):
                        try:
                            del ob.administrative_level
                            changed = True
                            self.log.debug('Landscape type deleted from %s' %
                                ob.absolute_url())
                        except AttributeError:
                            pass
                    if ob.hasLocalProperty('administrative_level'):
                        ob.del_localproperty('administrative_level')
                        changed = True
                        self.log.debug('Administrative level (local property) deleted from %s' %
                            ob.absolute_url())
                else:
                    if not hasattr(ob.aq_base, 'administrative_level'):
                        if administrative_level_localized:
                            self.log.debug('Landscape type set to "Unspecified" for %s' %
                                ob.absolute_url())
                            ob.set_localpropvalue('administrative_level', 'en',
                                    'Unspecified')
                        else:
                            self.log.debug('Administrative level set to local property "Unspecified" for %s' %
                                ob.absolute_url())
                            ob.administrative_level = 'Unspecified'
                        changed = True
                    else:
                        for key, values in administrative_replacements.items():
                            if ob.administrative_level in values:
                                self.log.debug(
                                    'Administrative level: replaced "%s" by "%s" for %s' % (
                                    ob.administrative_level, key, ob.absolute_url()))
                                ob.set_localpropvalue('administrative_level', 'en', key)
                                changed = True
                        if ob.administrative_level != ob.administrative_level.strip():
                            self.log.debug(
                                    'Administrative level: replaced "%s" by "%s" for %s' % (
                                ob.administrative_level, ob.administrative_level.strip(),
                                ob.absolute_url()))
                            ob.set_localpropvalue('administrative_level', 'en',
                                    ob.administrative_level.strip())
                            changed = True
                        if ob.administrative_level not in administrative_levels:
                            self.log.error('Unhandled administrative_level value %s on object %s'
                                    % (ob.administrative_level, ob.absolute_url()))

                if changed:
                    portal.recatalogNyObject(ob)
        return True
