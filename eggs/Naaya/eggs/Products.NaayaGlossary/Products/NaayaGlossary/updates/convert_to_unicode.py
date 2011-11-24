from naaya.core.utils import force_to_unicode

from Products.naayaUpdater.updates import UpdateScript

from Products.NaayaGlossary.constants import (NAAYAGLOSSARY_CENTRE_METATYPE,
                                              NAAYAGLOSSARY_FOLDER_METATYPE,
                                              NAAYAGLOSSARY_ELEMENT_METATYPE)


class ConvertToUnicode(UpdateScript):
    title = 'Convert glossary values to unicode'
    authors = ['Andrei Laza']
    creation_date = 'Nov 18, 2011'

    def convert_values_to_unicode(self, element, languages):
        title = getattr(element, 'title', u'')
        if not isinstance(title, unicode):
            self.log.debug('%s title: %s',
                    element.absolute_url(), title)
            element.title = force_to_unicode(title)

        for language in languages:
            value = getattr(element, language, u'')
            if isinstance(value, unicode):
                continue
            self.log.debug('%s %s: %s',
                    element.absolute_url(), language, value)
            setattr(element, language, force_to_unicode(value))

        for language in languages:
            def_attr = 'def_' + language
            value = getattr(element, def_attr, u'')
            if isinstance(value, unicode):
                continue
            self.log.debug('%s %s: %s',
                    element.absolute_url(), def_attr, value)
            setattr(element, def_attr, force_to_unicode(value))

    def _update(self, portal):
        for glossary in portal.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            languages = glossary.get_english_names()
            self.log.debug('Found glossary %s with languages %s',
                           glossary.absolute_url(), languages)
            for folder in glossary.objectValues(NAAYAGLOSSARY_FOLDER_METATYPE):
                self.convert_values_to_unicode(folder, languages)

                for element in folder.objectValues(NAAYAGLOSSARY_ELEMENT_METATYPE):
                    self.convert_values_to_unicode(element, languages)
        return True
