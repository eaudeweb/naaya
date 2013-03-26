from datetime import date
from Products.naayaUpdater.updates import UpdateScript

class UpdateMeetingSchema(UpdateScript):
    """ """
    title = 'Update Meeting pointer widgets for Groupware Sites'
    creation_date = 'Mar 26, 2013'
    authors = ['Cornel Nitu']
    description = ('Customize templates for survey_pointer-property, minutes_pointer-property and agenda_pointer-property')

    def _update(self, portal):
        schema_tool = portal.portal_schemas

        for schema in schema_tool.objectValues():
            if schema.id == 'NyMeeting':
                survey_pointer = getattr(schema, 'survey_pointer-property')
                survey_pointer.custom_template = 'portal_forms/schemawidget-NyMeeting-survey_pointer'

                minutes_pointer = getattr(schema, 'minutes_pointer-property')
                minutes_pointer.custom_template = 'portal_forms/schemawidget-NyMeeting-pointer'

                agenda_pointer = getattr(schema, 'agenda_pointer-property')
                agenda_pointer.custom_template = 'portal_forms/schemawidget-NyMeeting-pointer'

        return True
