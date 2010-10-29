from Products.naayaUpdater.updates import UpdateScript

class UpdateSurveyAnswer(UpdateScript):
    """ Update object attributes to unicode"""
    title = 'Update a Review Template Survey answer'
    creation_date = 'Oct 29, 2010'
    authors = ['Valentin Dumitru']
    description = 'Update a specific answer from the Naaya Survey at\
                    /tools/general_template/general-template'

    def _update(self, portal):
        self.update_answer(portal)
        return True

    def update_answer(self, portal):
        survey = getattr(portal.tools.general_template, 'general-template')
        the_answer = survey.answer_8089650866
        the_answer.w_confirmation = 1
        the_answer._p_changed = True