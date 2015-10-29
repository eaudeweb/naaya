from Products.naayaUpdater.updates import UpdateScript


class FixLinks(UpdateScript):
    title = 'Fix links in FLIS PBE terms'
    authors = ('Alex Eftimie')
    creation_date = 'Oct 29, 2015'
    description = (
        'Fix links in Foresight Dictionary imported from Forum to PBE'
    )

    def fix_def_links(self, element, languages):
        for language in languages:
            def_attr = 'def_' + language
            value = getattr(element, def_attr, u'')
            self.log.debug('%s %s: %s',
                           element.absolute_url(), def_attr, value)
            value = (
                value.replace('/nrc-flis/portal_glossary',
                              '/terms-and-definitions')
            )
            setattr(element, def_attr, force_to_unicode(value))

    def _update(self, portal):
        for glossary in portal.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            languages = glossary.get_english_names()
            self.log.debug('Found glossary %s with languages %s',
                           glossary.absolute_url(), languages)
            for folder in glossary.objectValues(NAAYAGLOSSARY_FOLDER_METATYPE):
                self.fix_def_links(folder, languages)

                for element in folder.objectValues(
                        NAAYAGLOSSARY_ELEMENT_METATYPE):
                    self.fix_def_links(element, languages)
        return True
