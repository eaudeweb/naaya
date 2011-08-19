class ExpnetMixin(object):
    def _is_chm_term(self, term):
        lang = self.gl_get_selected_language()
        lang_name = self.gl_get_language_name(lang)
        glossary = self._get_schema().getWidget('chm_terms').get_glossary()

        for gfolder in glossary.objectValues('Naaya Glossary Folder'):
            if gfolder.get_translation_by_language(lang_name) == term:
                return True
            for gelement in gfolder.objectValues('Naaya Glossary Element'):
                if gelement.get_translation_by_language(lang_name) == term:
                    return True
        return False

    def translate_chm_term(self, term, from_lang, to_lang):
        from_lang_name = self.gl_get_language_name(from_lang)
        to_lang_name = self.gl_get_language_name(to_lang)
        glossary = self._get_schema().getWidget('chm_terms').get_glossary()

        for gfolder in glossary.objectValues('Naaya Glossary Folder'):
            if gfolder.get_translation_by_language(from_lang_name) == term:
                return gfolder.get_translation_by_language(to_lang_name)
            for gelement in gfolder.objectValues('Naaya Glossary Element'):
                if gelement.get_translation_by_language(from_lang_name) == term:
                    return gelement.get_translation_by_language(to_lang_name)

        raise ValueError(term)

    def getChmTerms(self):
        if (not hasattr(self.aq_base, 'chm_terms')
                or not self.aq_base.chm_terms):
            return []
        remaining = self.chm_terms

        ret = []
        l = remaining.split(',')
        while l:
            for i in range(1, len(l)+1):
                term = (','.join(l[:i])).strip()
                if self._is_chm_term(term):
                    ret.append(term)
                    l = l[i:]
                    break
            else:
                l = l[1:] # consume one element

        return ret

    def topics(self):
        default_language = self.gl_get_default_language()
        lang = self.gl_get_selected_language()

        ret = []
        for term in self.getChmTerms():
            try:
                ret.append(self.translate_chm_term(term, lang, default_language))
            except ValueError:
                pass
        return ret
