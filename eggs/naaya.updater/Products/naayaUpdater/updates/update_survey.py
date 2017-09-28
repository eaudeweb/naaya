from Products.naayaUpdater.updates import UpdateScript

class UpdateSurvey(UpdateScript):
    title='Update new property for Naaya Mega Survey'
    descrtiption = 'Adde new allow_multiple_answers with default value of 0 to'
    'Naaya Mega Survey objects'
    def _update(self, portal):
        """ """
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type='Naaya Mega Survey'):
            survey_ob = brain.getObject()
            if not hasattr(survey_ob, 'allow_multiple_answers'):
                survey_ob.allow_multiple_answers = 0
                self.log.debug('Added property allow_multiple_answers to %r',
                               survey_ob.absolute_url())
        return True
