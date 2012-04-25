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
publication_freq = _load_json("refdata/publication_freq.json")
eu_countries_list = _load_json("refdata/european_countries_list.json")
countries_list = _load_json("refdata/countries_list.json")
languages_list = _load_json("refdata/languages_list.json")
indicators_estimation = _load_json("refdata/indicators_estimation.json")

ReportSchema = fl.Dict.with_properties(widget="schema") \
                      .of(

    CommonDict.named('header') \
              .using(label=u"HEADER INFORMATION") \
              .of(
        CommonEnum.named('country') \
                  .using(label=u"Country") \
                  .with_properties(css_class="chzn-select",
                                   field_id="country_sel",
                                   widget="chosen_select",
                                   multiple="",
                                   data_placeholder="Select countries") \
                  .valued(*countries_list),
        fl.String.named('soer_cover') \
                 .using(label=u"Copy of SOER cover")
    ),

    CommonDict.named('details') \
              .using(label=u"REPORT DETAILS") \
              .of(

        fl.String.named('original_name') \
                 .using(label=u"Name"),

        CommonEnum.named('original_language') \
                 .using(label=u"Original Language") \
                 .valued(*languages_list),

        fl.String.named('english_name') \
                 .using(label=u"Name (in English)"),

        fl.Date.named('date_of_publication') \
                 .using(label=u"Date of publication") \
                 .including_validators(Converted(incorrect=u"%(label)s is not "
                                                            "a valid date")),

        fl.String.named('publisher') \
                 .using(label=u"Published by"),

        CommonEnum.named('freq_of_pub') \
                  .using(label=u"Frequency of publication") \
                  .valued(*sorted(publication_freq.keys())),
    ),

    CommonDict.named('format') \
              .using(label=u"FORMAT & ACCESSIBILITY") \
              .of(

        CommonEnum.named('format') \
                  .using(label=u"Format") \
                  .valued(*sorted(report_formats.keys())),

        fl.Integer.named('no_of_pages') \
                 .using(label=u"No. of pages (main SOE report)"),

        CommonEnum.named("separate_summary") \
                  #TODO implement values in json list
                  .valued(*(['Yes', 'No', 'Unknown'])) \
                     .using(label=u"Separate summary report?"),

        CommonEnum.named('lang_of_pub') \
                 .using(label=u"Languages of publication") \
                 .valued(*languages_list),

        fl.Dict.named('availability') \
               .with_properties(widget="options_with_labels") \
                  .using(label=u"Availability")\
                  .of(

            CommonBoolean.named("paper_only") \
                         .using(label=u"Paper only"),

            CommonBoolean.named("web") \
                         .using(label=u"web"),

            fl.String.named("url") \
                         .using(label=u"URL"),

            CommonBoolean.named("free") \
                         .using(label=u"free"),

            CommonBoolean.named("with_costs") \
                         .using(label=u"with costs"),
        ),

        CommonBoolean.named("registered_eionet") \
                         .using(label=u"Registered in Eionet SERIS before"),

        fl.String.named("short_description") \
                 .using(label=u"Short description from SERIS (old):") \
                 .with_properties(widget="textarea"),

        fl.String.named("table_of_contents") \
                 .using(label=u"Overview of table of contents and"
                               " indicators in report") \
                 .with_properties(widget="textarea"),

    )
)


indicators_usage = _load_json("refdata/indicators_usage.json")
topics_ratings = _load_json("refdata/topics_ratings.json")
evaluation_methods = _load_json("refdata/evaluation_methods.json")

CommonTopicsEnum = fl.Enum.using(optional=True) \
                          .with_properties(widget="topics_radioselect") \
                          .valued(*sorted(topics_ratings.keys()))

CommonIndicatorsEnum = fl.Enum.using(optional=True) \
                          .with_properties(widget="indicators_radioselect") \
                          .valued(*sorted(topics_ratings.keys()))

CommonTopicsDict = CommonDict.with_properties(widget="topics_columns") \
                             .of(

                        CommonTopicsEnum.named('focus') \
                                        .using(label=u"Focus"),

                        CommonTopicsEnum.named('indicators') \
                                  .using(label=u"Indicators"),
                   )

SerisReviewSchema = fl.Dict.with_properties(widget="schema") \
                           .of(

    fl.Integer.named('report_id') #TODO shouldn't be editable
              .with_properties(widget='hidden') \
              .using(label="Report id"),

    CommonDict.named('links') \
              .using(label=u"LINKS TO OTHER SoE REPORTS") \
              .of(
        fl.Dict.named('reference') \
               .using(label=u"Reference/links to:") \
               .with_properties(widget="subgroup") \
                  .of(

            CommonBoolean.named('global_level') \
                         .using(label=u"Global-level SOER's (e.g. UNEP GEO)?"),

            CommonBoolean.named('european_level') \
                         .using(label=u"European-level SOER's (e.g. EEA SOER)?"),

            CommonBoolean.named('national_level') \
                         .using(label=u"National-level SOER's (e.g. other country)?"),

            CommonBoolean.named('sub_national_level') \
                         .using(label=u"Sub-national-level SOER's (e.g. regional)?"),
        ),
                     
        CommonBoolean.named('key_findings') \
                     .using(label=u"Reference/links to key findings "
                                   "of the country's previous SOER?"),
    ),

    CommonDict.named('structure') \
              .using(label=u"STRUCTURE") \
              .of(

        fl.Dict.named('reference') \
                .using(label=u"DPSIR framework:") \
               .with_properties(widget="subgroup") \
                  .of(

            CommonBoolean.named('basis_structure') \
                         .using(label=u"Basis for report structure?"),
        ),

        CommonBoolean.named('indicator_based') \
                     .using(label=u"Indicator-based report?"),

        CommonEnum.named('indicators_estimation') \
                  .valued(*sorted(indicators_estimation.keys())) \
                  .using(label=u"Indicators:"),

        CommonBoolean.named('eea_indicators') \
                     .using(label=u"EEA indicators used?"),

        fl.String.named("eea_indicators_estimated_no") \
                 .using(label=u"Estimated number?"),

        fl.Dict.named('indicators_usage') \
               .using(label=u"How are indicators used?") \
               .with_properties(widget="subgroup") \
               .of(

            CommonIndicatorsEnum.named('to_compare_countries') \
                            .valued(*sorted(indicators_usage.keys())) \
                            .using(label=u"To compare with other countries/EU?"),

            CommonIndicatorsEnum.named('to_compare_subnational') \
                            .valued(*sorted(indicators_usage.keys())) \
                            .using(label=u"To compare at sub-national level?"),

            CommonIndicatorsEnum.named('to_assess_progress') \
                            .valued(*sorted(indicators_usage.keys())) \
                            .using(label=u"To asses progress to target/threshold?"),

            CommonIndicatorsEnum.named('to_evaluate') \
                            .valued(*sorted(indicators_usage.keys())) \
                            .using(label=u"To rank/evaluate (e.g. with 'smileys')?"),

            CommonEnum.named("related_reports_name") \
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

            CommonTopicsDict.named('coast_and_seas') \
                            .using(label=u"Coast and seas"),

            CommonTopicsDict.named('specific_regions') \
                            .using(label=u"Specific regions"),

            CommonTopicsDict.named('urban_environment') \
                            .using(label=u"Urban environment"),

            CommonTopicsDict.named('other_radio') \
                            .using(label=u"............(input field)"),
        ),

        CommonDict.named('env_issues') \
                  .using(label=u"Environmental issues") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

                CommonTopicsDict.named('air_pollution') \
                                .using(label=u"Air pollution"),

                CommonTopicsDict.named('biodiversity') \
                                .using(label=u"Biodiversity"),

                CommonTopicsDict.named('chemicals') \
                                .using(label=u"Chemicals"),

                CommonTopicsDict.named('climate_change') \
                                .using(label=u"Climate change"),

                CommonTopicsDict.named('env_and_health') \
                                .using(label=u"Environment and health"),

                CommonTopicsDict.named('land_use') \
                                .using(label=u"Land use"),

                CommonTopicsDict.named('natural_resources') \
                                .using(label=u"Natural resources"),

                CommonTopicsDict.named('noise') \
                                .using(label=u"Noise"),

                CommonTopicsDict.named('soil') \
                                .using(label=u"Soil"),
                                
                CommonTopicsDict.named('waste_and_resources') \
                                .using(label=u"Waste and material resources"),

                CommonTopicsDict.named('water') \
                                .using(label=u"Water"),

                CommonTopicsDict.named('other_issues') \
                                .using(label=u"Various other issues"),

                CommonTopicsDict.named('other_radio') \
                                .using(label=u"............(input field)"),
        ),

        CommonDict.named('sectors_and_activities') \
                  .using(label=u"Sectors and activities") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

            CommonTopicsDict.named('agriculture') \
                            .using(label=u"Agriculture"),

            CommonTopicsDict.named('energy') \
                            .using(label=u"Energy"),

            CommonTopicsDict.named('fisheries') \
                            .using(label=u"Fisheries"),

            CommonTopicsDict.named('household_consumption') \
                            .using(label=u"Household consumption"),

            CommonTopicsDict.named('industry') \
                            .using(label=u"Industry"),

            CommonTopicsDict.named('green_economy') \
                            .using(label=u"Green economy"),

            CommonTopicsDict.named('tourism') \
                            .using(label=u"Tourism"),

            CommonTopicsDict.named('transport') \
                            .using(label=u"Transport"),

            CommonTopicsDict.named('other_radio') \
                            .using(label=u"............(input field)"),
        ),

        CommonDict.named('across_env') \
                  .using(label=u"Across environmental issues and sectors") \
                  .with_properties(widget="topics_subgroup") \
                  .of(

            CommonTopicsDict.named('env_technology') \
                            .using(label=u"Environmental technology"),

            CommonTopicsDict.named('policy_instruments') \
                            .using(label=u"Policy instruments"),

            CommonTopicsDict.named('env_scenarios') \
                            .using(label=u"Environmental scenarios"),

            CommonTopicsDict.named('other_radio') \
                            .using(label=u"............(input field)"),
        ),
    ),
)
