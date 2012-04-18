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
CommonBoolean = fl.Boolean.using(optional=False).with_properties(widget="checkbox")

report_formats = _load_json("refdata/report_formats.json")

ReportSchema = fl.Dict.with_properties(widget="schema") \
                      .of(

    CommonEnum.named('country') \
             .using(label=u"Country"),

    CommonDict.named('details') \
              .using(label=u"REPORT DETAILS") \
              .of(

        fl.String.named('original_name') \
                 .using(label=u"Name"),

        fl.String.named('original_language') \
                 .using(label=u"Original Language"),

        fl.String.named('english_name') \
                 .using(label=u"Name (in English)"),

        fl.Date.named('publication_date') \
                 .using(label=u"Date of publication") \
                 .including_validators(Converted(incorrect=u"%(label)s is not "
                                                            "a valid date")),

        fl.String.named('publisher') \
                 .using(label=u"Published by"),
    ),

    CommonDict.named('format') \
              .using(label=u"FORMAT & ACCESSIBILITY") \
              .of(

        CommonEnum.named('Format') \
               .valued(*sorted(report_formats.keys())),

        fl.Integer.named('no_of_pages') \
                 .using(label=u"No. of pages (main SOE report)"),

        CommonBoolean.named("separate_summary") \
                     .using(label=u"Separate summary report?"),

        CommonBoolean.named("separate_indicator") \
                     .using(label=u"Separate summary report? "),

        fl.String.named("separate_indicator_report_name") \
                .using(label=u"If yes, name of report:"),

        CommonBoolean.named("related_reports") \
                     .using(label=u"Other directly related reports? "
                                   "If yes, name of report/s:"),

        fl.String.named("related_reports_name") \
                .using(label=u"If yes, name of report/s:"),

        CommonEnum.named('languages') \
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

        fl.String.named("latest_year_seris") \
                .using(label=u"If No, latest year in SERIS:"),

        fl.String.named('web_page') \
                 .using(label=u"Web page"),
    )
)


indicators_usage = _load_json("refdata/indicators_usage.json")
uncertainty_methods = _load_json("refdata/uncertainty_methods.json")

SerisReviewSchema = fl.Dict.with_properties(widget="schema") \
                           .of(

    fl.Integer.named('report_id'), #TODO shouldn't be editable

    CommonDict.named('links') \
              .using(label=u"LINKS TO OTHER SoE REPORTS") \
              .of(

        CommonBoolean.named('global') \
                     .using(label=u"Global-level SOER's (e.g. UNEP GEO)?"),

        CommonBoolean.named('european') \
                     .using(label=u"European-level SOER's (e.g. EEA SOER)?"),

        CommonBoolean.named('national') \
                     .using(label=u"National-level SOER's (e.g. other country)?"),

        CommonBoolean.named('sub_national') \
                     .using(label=u"Sub-national-level SOER's (e.g. regional)?"),
                     
        CommonBoolean.named('key_findings') \
                     .using(label=u"Reference/links to key findings "
                                   "of the country's previous SOER?"),
    ),

    CommonDict.named('structure') \
              .using(label=u"STRUCTURE") \
              .of(

        CommonBoolean.named('basis') \
                     .using(label=u"Basis for report structure?"),

        CommonBoolean.named('referenced') \
                     .using(label=u"Referenced (ie. keyword search)?"),

        CommonBoolean.named('indicator_based') \
                     .using(label=u"Indicator-based report?"),

        fl.String.named("no_of_indicators") \
                .using(label=u"No. of indicators:"),

        fl.String.named("indicators_per_page") \
                .using(label=u"Indicators per page:"),

        CommonBoolean.named('eea_indicators') \
                     .using(label=u"EEA indicators used?"),

        fl.String.named("eea_indicators_estimated_no") \
                .using(label=u"Estimated number?"),

        CommonEnum.named('to_compare_countries') \
                  .valued(*sorted(indicators_usage.keys())) \
                  .using(label=u"To compare with other countries/EU?"),

        CommonEnum.named('to_compare_subnational') \
                  .valued(*sorted(indicators_usage.keys())) \
                  .using(label=u"To compare at sub-national level?"),

        CommonEnum.named('to_assess_progress') \
                  .valued(*sorted(indicators_usage.keys())) \
                  .using(label=u"To asses progress to target/threshold?"),

        CommonEnum.named('to_evaluate') \
                  .valued(*sorted(indicators_usage.keys())) \
                  .using(label=u"To rank/evaluate (e.g. with 'smileys')?"),

        fl.String.named("related_reports_name") \
                .using(label=u"If yes, how?"),

        CommonBoolean.named('dedicated_chapter') \
                  .using(label=u"Dedicated chapter"),

        CommonBoolean.named('dedicated_method') \
                     .using(label=u"Dedicated method"),

        CommonEnum.named('uncertainty') \
                  .valued(*sorted(uncertainty_methods.keys())) \
                  .using(label=u"Uncertainty method used:"),

        fl.String.named("method_details") \
                .using(label=u"Details:"),
    )

)
