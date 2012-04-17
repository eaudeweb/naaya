import flatland as fl
import os
import json
import database
from flatland.validation import Converted

def _load_json(name):
    with open(os.path.join(os.path.dirname(__file__), name), "rb") as f:
        return json.load(f)

CommonEnum = fl.Enum.using(optional=True).with_properties(widget="select")
CommonDict = fl.Dict.with_properties(widget="group")
CommonBoolean = fl.Boolean.using(optional=True).with_properties(widget="checkbox")

report_formats = _load_json("refdata/report_formats.json")

ReportSchema = fl.Dict.with_properties(widget="schema") \
                      .of(
    fl.String.named('country') \
             .using(label=u"Country"),
    fl.String.named('name') \
             .using(label="Name of report"),

    CommonDict.named('details') \
              .using(label=u"REPORT DETAILS") \
              .of(
        fl.String.named('title') \
                 .using(label=u"Title"),
        fl.Date.named('publication_date') \
                 .using(label=u"Date of publication") \
                 .including_validators(Converted(incorrect=u"%(label)s is not "
                                                            "a valid date")),
        fl.String.named('publisher') \
                 .using(label=u"Published by"),
    ),

    CommonDict.named('format') \
              .using(label="FORMAT & ACCESSIBILITY") \
              .of(
        CommonEnum.named('Format') \
               .valued(*sorted(report_formats.keys())),
        fl.Scalar.named('no_of_pages') \
                 .using(label=u"No. of pages (main SOE report)"),
        CommonBoolean.named("separate_summary") \
                     .using(label=u"Separate summary report?"),
        CommonBoolean.named("separate_indicator") \
                     .using(label=u"Separate summary report?\nIf yes, name of report:"),
        CommonBoolean.named("related_reports") \
                     .using(label=u"Other directly related reports?\nIf yes, name of report/s:"),
        fl.String.named('languages') \
                 .using(label=u"Languages of publication"),
        CommonDict.named('availability') \
                  .using(label=u"Availability")\
                  .of(
            CommonBoolean.named("internet") \
                         .using(label=u"Internet (portal)"),
            CommonBoolean.named("electronic") \
                         .using(label=u"Electronic copy (portal)"),
            CommonBoolean.named("paper_free") \
                         .using(label=u"Paper copy (free)"),
            CommonBoolean.named("paper_purchase") \
                         .using(label=u"Paper copy (purchase)"),
        ),
        CommonBoolean.named("updated_eionet") \
                         .using(label=u"Updated in Eionet SERIS"),
        fl.String.named('web_page') \
                 .using(label=u"Web page"),
    )
)


SerisReviewSchema = fl.Dict.with_properties(widget="group") \
                           .of(

    fl.Integer.named('report_id'),

    fl.Dict.named('links') \
           .of(

        fl.Boolean.named('global'),

        fl.Boolean.named('european'),

        fl.Boolean.named('national'),

    )

)
"""
class ReportSchema(_ReportSchema):

    @property
    def value(self):
        return Report(super(ReportSchema, self).value)

class Report(dict):

    id = None

    @staticmethod
    def from_flat(report_row):
        report = ReportSchema.from_flat(report_row).value
        report.id = report_row.id
        return report

    @classmethod
    def get_or_404(cls, report_id):
        return cls.from_flat(database.get_report_or_404(report_id))
"""


