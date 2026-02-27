class ExpnetMixin(object):
    def getChmTerms(self):
        if (not hasattr(self.aq_base, 'chm_terms')
                or not self.aq_base.chm_terms):
            return []
        separator = self._get_schema().getWidget('chm_terms').separator
        return self.chm_terms.split(separator)

    topics = getChmTerms
