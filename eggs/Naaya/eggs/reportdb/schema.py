import flatland as fl
import os
import json
import database
import datetime
from flatland.validation import Converted
from file_upload import CommonFile


def _load_json(name):
    with open(os.path.join(os.path.dirname(__file__), name), "rb") as f:
        return json.load(f)


def register_handler_for_empty():
    """
    Flatland doesn't generate "is required" messages for invalid empty
    fields so we need to add the messages ourselves.
    """
    from flatland.signals import validator_validated
    from flatland.schema.base import NotEmpty
    def validated(sender, element, result, **kwargs):
        if not result:
            msg = u"%s is mandatory" % element.label
            element.add_error(msg)
    validator_validated.connect(validated, NotEmpty, weak=False)


CommonString = fl.String.using(optional=True)
CommonEnum = fl.Enum.using(optional=True).with_properties(widget="select")
CommonDict = fl.Dict.with_properties(widget="group")
CommonBoolean = fl.Boolean.with_properties(widget="checkbox")

report_formats = _load_json("refdata/report_formats.json")
publication_years = [str(year) for year in xrange(1990,
                                           datetime.datetime.now().year+1)]
publication_freq = _load_json("refdata/publication_freq.json")
eu_countries_list = _load_json("refdata/european_countries_list.json")
countries_list = _load_json("refdata/countries_list.json")
languages = _load_json("refdata/languages_list.json")
language_codes = [pair[1] for pair in
                  sorted([(v,k) for (k,v) in languages.items()])]

indicators_estimation = _load_json("refdata/indicators_estimation.json")

ReportSchema = fl.Dict.with_properties(widget="schema") \
                      .of(

    CommonDict.named('header') \
              .using(label=u"") \
              .of(

        fl.List.named('country') \
               .using(label=u"Country") \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                help=u"Region/sub-national?",
                                placeholder="Select countries ...") \
               .of(

            CommonEnum.valued(*countries_list)

        ),

        CommonFile.named('soer_cover') \
                  .using(label=u"Copy of SOER cover") \
                  .with_properties(widget_image=True),

        CommonString.named('uploader') \
                    .using(label=u"Factsheet prepared by",
                           optional=False),

        CommonString.named('upload_date') \
                    .with_properties(field_type='hidden') \
                    .using(label=u"Latest update")

    ),

    CommonDict.named('details') \
              .using(label=u"REPORT DETAILS") \
              .of(

        CommonString.named('original_name') \
                    .using(label=u"Title",
                           optional=False)
                    .with_properties(css_class="input-big"),

        CommonEnum.named('original_language') \
                  .using(label=u"Original Language",
                         optional=False) \
                  .with_properties(value_labels=languages,
                                   placeholder="Select a language ...",
                                   widget_chosen=True) \
                  .valued(*language_codes),

        CommonString.named('english_name') \
                    .using(label=u"Title (in English)") \
                    .with_properties(css_class="input-big"),

        CommonEnum.named('date_of_publication') \
                    .using(label=u"Date of publication") \
                    .valued(*publication_years) \
                    .with_properties(css_class="input-small"),

        CommonString.named('publisher') \
                    .using(label=u"Published by") \
                    .with_properties(css_class="input-medium"),

        CommonEnum.named('freq_of_pub') \
                  .using(label=u"Frequency of publication") \
                  .valued(*sorted(publication_freq.keys())),
    ),

    CommonDict.named('format') \
              .using(label=u"FORMAT & ACCESSIBILITY") \
              .of(

        CommonEnum.named('format') \
                  .using(label=u"Format") \
                  .valued(*report_formats),

        fl.Integer.named('no_of_pages') \
                  .using(label=u"No. of pages (main SOE report)",
                         optional=True) \
                  .with_properties(css_class="input-small"),

        CommonEnum.named("separate_summary") \
                  #TODO implement values in json list
                  .valued(*(['Yes', 'No', 'Unknown'])) \
                  .using(label=u"Separate summary report?"),

        fl.List.named('lang_of_pub') \
               .using(label=u"Languages of publication") \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                placeholder="Select languages ...") \
               .of(

            CommonEnum.valued(*language_codes) \
                      .with_properties(value_labels=languages)

        ),

        fl.Dict.named('availability') \
               .with_properties(widget="options_with_labels") \
               .using(label=u"Availability")\
               .of(

            fl.Enum.named('paper_or_web') \
                   .with_properties(widget="radioselect") \
                   .valued(*(["paper only", "web"])) \
                   .using(label=u""),

            CommonString.named("url") \
                        .with_properties(widget="url") \
                        .using(label=u"URL"),

            fl.Enum.named('costs') \
                   .with_properties(widget="radioselect") \
                   .valued(*(["free", "with costs"])) \
                   .using(label=u""),

        ),

        CommonBoolean.named("registered_eionet") \
                     .with_properties(reversed="True") \
                     .using(label=u"Registered in Eionet SERIS before?"),

    )
)


indicators_usage = _load_json("refdata/indicators_usage.json")
topics_ratings = _load_json("refdata/topics_ratings.json")
evaluation_methods = _load_json("refdata/evaluation_methods.json")

TopicEnum = fl.Enum.using(optional=True) \
                   .with_properties(widget="topics_radioselect", 
                                    extra_topic="True") \
                   .valued(*topics_ratings)

IndicatorEnum = fl.Enum.using(optional=True) \
                  .with_properties(widget="indicators_radioselect") \
                  .valued(*topics_ratings)

TopicDict = CommonDict.with_properties(widget="topics_columns") \
                      .of(

    TopicEnum.named('focus') \
             .with_properties(css_class="focus-column",
                              add_empty_td="true") \
             .using(label=u"Focus"),

    TopicEnum.named('indicators') \
             .with_properties(css_class="indicators-column") \
             .using(label=u"Indicators"),

)


EeaTopicDict = TopicDict.with_properties(eea_theme_link=True)


SerisReviewSchema = fl.Dict.with_properties(widget="schema") \
                           .of(

    fl.Integer.named('report_id') #TODO shouldn't be editable
              .with_properties(field_type='hidden') \
              .using(label="Report id"),

    CommonDict.named('links') \
              .using(label=u"LINKS TO OTHER SoE REPORTS") \
              .of(
        fl.Dict.named('reference') \
               .using(label=u"Reference/links to:") \
               .with_properties(widget="reference_group") \
               .of(

            CommonBoolean.named('global_level') \
                         .using(label=u"Global-level SOER's?") \
                         .with_properties(help=u"(e.g. UNEP GEO)"),

            CommonBoolean.named('european_level') \
                         .using(label=u"European-level SOER's?") \
                         .with_properties(help=u"(e.g. EEA SOER)"),

            CommonBoolean.named('national_level') \
                         .using(label=u"National-level SOER's?") \
                         .with_properties(help=u"(e.g. other country)"),

            CommonBoolean.named('sub_national_level') \
                         .using(label=u"Sub-national-level SOER's?") \
                         .with_properties(help=u"(e.g. regional)"),
        ),

        CommonBoolean.named('key_findings') \
                     .using(label=u"Reference/links to key findings "
                                   "of the country's previous SOER?") \
                     .with_properties(reversed="True"),
    ),

    CommonDict.named('structure') \
              .using(label=u"STRUCTURE") \
              .of(

        fl.Dict.named('reference') \
               .using(label=u"DPSIR framework:") \
               .with_properties(widget="subgroup") \
               .of(

            CommonBoolean.named('basis_structure') \
                         .using(label=u"Basis for report structure?") \
                         .with_properties(reversed="True"),
        ),

        fl.Enum.named('indicator_based') \
               .with_properties(widget="radioselect") \
               .valued(*(["Yes", "No"])) \
               .using(label=u"Indicator-based report?",
                         optional=True),

        CommonEnum.named('indicators_estimation') \
                  .valued(*indicators_estimation) \
                  .using(label=u"Indicators estimation:"),

        fl.Enum.named('eea_indicators') \
               .with_properties(widget="radioselect") \
               .valued(*(["Yes", "No"])) \
               .using(label=u"EEA indicators used?",
                         optional=True),

        CommonString.named("eea_indicators_estimated_no") \
                    .using(label=u"Estimated number?") \
                    .with_properties(css_class="input-small"),

        fl.Dict.named('indicators_usage') \
               .using(label=u"How are indicators used?") \
               .with_properties(widget="indicators_group", hidden_label="True") \
               .of(

            IndicatorEnum.named('to_compare_countries') \
                         .valued(*indicators_usage) \
                         .using(label=u"To compare with other countries/EU?"),

            IndicatorEnum.named('to_compare_subnational') \
                         .valued(*indicators_usage) \
                         .using(label=u"To compare at sub-national level?"),

            IndicatorEnum.named('to_assess_progress') \
                         .valued(*indicators_usage) \
                         .using(label=u"To asses progress to target/threshold?"),

            IndicatorEnum.named('to_evaluate') \
                         .valued(*indicators_usage) \
                         .using(label=u"To rank/evaluate (e.g. with 'smileys')?"),

            CommonEnum.named("evaluation_method") \
                      .valued(*sorted(evaluation_methods.keys())) \
                      .using(label=u"If yes, how?"),
        ),

        fl.Dict.named('uncertainty_addressed') \
               .using(label=u"Uncertainty addressed?") \
               .with_properties(widget="subgroup") \
               .of(

            CommonBoolean.named('dedicated_chapter') \
                         .using(label=u"Dedicated chapter"),

            CommonBoolean.named('dedicated_method') \
                         .using(label=u"Dedicated method"),
        ),
    ),

    fl.Dict.named('topics') \
           .using(label=u"TOPICS COVERED") \
           .with_properties(widget="topics_group") \
           .of(

        CommonDict.named('env_regions') \
                  .using(label=u"Environment in different"
                             " regions and specific areas") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

            EeaTopicDict.named('coast_sea') \
                        .using(label=u"Coast and seas"),

            EeaTopicDict.named('regions') \
                        .using(label=u"Specific regions"),

            EeaTopicDict.named('urban') \
                        .using(label=u"Urban environment"),

            CommonDict.named('extra_topic') \
                      .with_properties(extra_topic="True") \
                      .of(

                CommonString.named('extra_topic_input') \
                            .with_properties(hidden_label="True",
                                             css_class="input-medium"),

                TopicDict.named('other_radio') \
                         .with_properties(enclosed_in_div="False", 
                                          hidden_label="True"),
            ),
        ),

        CommonDict.named('env_issues') \
                  .using(label=u"Environmental issues") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

            EeaTopicDict.named('air') \
                        .using(label=u"Air pollution"),

            EeaTopicDict.named('biodiversity') \
                        .using(label=u"Biodiversity"),

            EeaTopicDict.named('chemicals') \
                        .using(label=u"Chemicals"),

            EeaTopicDict.named('climate') \
                        .using(label=u"Climate change"),

            EeaTopicDict.named('human') \
                        .using(label=u"Environment and health"),

            EeaTopicDict.named('landuse') \
                        .using(label=u"Land use"),

            EeaTopicDict.named('natural') \
                        .using(label=u"Natural resources"),

            EeaTopicDict.named('noise') \
                        .using(label=u"Noise"),

            EeaTopicDict.named('soil') \
                        .using(label=u"Soil"),

            EeaTopicDict.named('waste') \
                        .using(label=u"Waste and material resources"),

            EeaTopicDict.named('water') \
                        .using(label=u"Water"),

            EeaTopicDict.named('other_issues') \
                        .using(label=u"Various other issues"),

            CommonDict.named('extra_topic') \
                      .with_properties(extra_topic="True") \
                      .of(

                CommonString.named('extra_topic_input') \
                            .with_properties(hidden_label="True",
                                             css_class="input-medium"),

                TopicDict.named('other_radio') \
                         .with_properties(extra_topic="True", 
                                          hidden_label="True") \
            ),

        ),

        CommonDict.named('sectors_and_activities') \
                  .using(label=u"Sectors and activities") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

            EeaTopicDict.named('agriculture') \
                        .using(label=u"Agriculture"),

            EeaTopicDict.named('energy') \
                        .using(label=u"Energy"),

            EeaTopicDict.named('fishery') \
                        .using(label=u"Fisheries"),

            EeaTopicDict.named('households') \
                        .using(label=u"Household consumption"),

            EeaTopicDict.named('industry') \
                        .using(label=u"Industry"),

            EeaTopicDict.named('economy') \
                        .using(label=u"Green economy"),

            EeaTopicDict.named('tourism') \
                        .using(label=u"Tourism"),

            EeaTopicDict.named('transport') \
                        .using(label=u"Transport"),

            CommonDict.named('extra_topic') \
                      .with_properties(extra_topic="True") \
                      .of(

                CommonString.named('extra_topic_input') \
                            .with_properties(hidden_label="True",
                                             css_class="input-medium"),

                TopicDict.named('other_radio') \
                         .with_properties(extra_topic="True", 
                                          hidden_label="True") \
            ),
        ),

        CommonDict.named('across_env') \
                  .using(label=u"Across environmental issues and sectors") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

            EeaTopicDict.named('technology') \
                        .using(label=u"Environmental technology"),

            EeaTopicDict.named('policy') \
                        .using(label=u"Policy instruments"),

            EeaTopicDict.named('scenarios') \
                        .using(label=u"Environmental scenarios"),

            CommonDict.named('extra_topic') \
                      .with_properties(extra_topic="True") \
                      .of(

                CommonString.named('extra_topic_input') \
                            .with_properties(hidden_label="True",
                                             css_class="input-medium"),

                TopicDict.named('other_radio') \
                         .with_properties(extra_topic="True", 
                                          hidden_label="True") \
            ),
        ),

    ),

    CommonString.named("short_description") \
                .using(label=u"Short description from SERIS (old):") \
                .with_properties(widget="textarea"),

    CommonString.named("table_of_contents") \
                .using(label=u"Overview of table of contents and "
                              "indicators in report") \
                .with_properties(widget="textarea"),

)
