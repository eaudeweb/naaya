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

ReportSchema = fl.Dict.with_properties(widget="schema") \
                      .of(

    CommonEnum.named('country') \
              .using(label=u"Country") \
              .valued(*sorted(eu_countries_list.keys())),

    CommonDict.named('details') \
              .using(label=u"REPORT DETAILS") \
              .of(

        fl.String.named('original_name') \
                 .using(label=u"Name"),

        fl.String.named('original_language') \
                 .using(label=u"Original Language"),

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

    CommonDict.named('format_section') \
              .using(label=u"FORMAT & ACCESSIBILITY") \
              .of(

        CommonEnum.named('format') \
                  .using(label=u"Format") \
                  .valued(*sorted(report_formats.keys())),

        fl.Integer.named('no_of_pages') \
                 .using(label=u"No. of pages (main SOE report)"),

        CommonBoolean.named("separate_summary") \
                     .using(label=u"Separate summary report?"),

        CommonEnum.named('lang_of_pub') \
                 .using(label=u"Languages of publication"),

        fl.Dict.named('availability') \
               #TODO make a special widget to display properly
               #.with_properties(widget="options_with_labels") \
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

        CommonBoolean.named("updated_eionet") \
                         .using(label=u"Registered in Eionet SERIS before"),
    )
)


indicators_usage = _load_json("refdata/indicators_usage.json")
topics_ratings = _load_json("refdata/topics_ratings.json")

CommonTopicsEnum = fl.Enum.using(optional=True) \
                          .with_properties(widget="radioselect") \
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
              .using(label="Report id"),

    CommonDict.named('links') \
              .using(label=u"LINKS TO OTHER SoE REPORTS") \
              .of(
        fl.Dict.named('reference') \
               .with_properties(widget="group")
                  .of(

            CommonBoolean.named('global') \
                         .using(label=u"Global-level SOER's (e.g. UNEP GEO)?"),

            CommonBoolean.named('european') \
                         .using(label=u"European-level SOER's (e.g. EEA SOER)?"),

            CommonBoolean.named('national') \
                         .using(label=u"National-level SOER's (e.g. other country)?"),

            CommonBoolean.named('sub_national') \
                         .using(label=u"Sub-national-level SOER's (e.g. regional)?"),
        ),
                     
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

        fl.String.named("method_details") \
                .using(label=u"Details:"),
    ),

    fl.Dict.named('topics') \
           .with_properties(widget="subgroup") \
           .using(label=u"TOPICS COVERED") \
           .of(

        CommonDict.named('media') \
               .using(label=u"Environmental media") \
               .of(

            CommonTopicsDict.named('air') \
                            .using(label=u"Air"),

            CommonTopicsDict.named('land') \
                            .using(label=u"Land"),

            CommonTopicsDict.named('soil') \
                            .using(label=u"Soil"),

            CommonTopicsDict.named('inland_waters') \
                            .using(label=u"Inland waters (incl. rivers)"),

            CommonTopicsDict.named('coastal_waters') \
                            .using(label=u"Coastal waters and marine"),

            CommonTopicsDict.named('urban_environment') \
                            .using(label=u"Cities & urban environment"),
        ),

        CommonDict.named('themes') \
               .using(label=u"Environmental themes") \
               .of(

                CommonTopicsDict.named('climate_change') \
                                .using(label=u"Climate change"),

                CommonTopicsDict.named('climate_science') \
                                .using(label=u"Climate science and impacts"),

                CommonTopicsDict.named('mitigation') \
                                .using(label=u"Mitigation (reducing pressure)"),

                CommonTopicsDict.named('adaptation') \
                                .using(label=u"Adaptation (adapting to impact)"),

                CommonTopicsDict.named('climate_other') \
                                .using(label=u"Other - specify"),

                CommonTopicsDict.named('nature') \
                                .using(label=u"Nature and biodiversity"),

                CommonTopicsDict.named('species') \
                                .using(label=u"Species (flora and fauna)"),

                CommonTopicsDict.named('habitats') \
                                .using(label=u"Habitats and biotopes"),

                CommonTopicsDict.named('conservation') \
                                .using(label=u"Nature conservation"),
                                
                CommonTopicsDict.named('nature_other') \
                                .using(label=u"Other - specify"),

                CommonTopicsDict.named('resources') \
                                .using(label=u"Natural resources and waste"),

                CommonTopicsDict.named('consumption') \
                                .using(label=u"Consumption/Urbanisation"),

                CommonTopicsDict.named('material_flow') \
                                .using(label=u"Material flow"),

                CommonTopicsDict.named('waste') \
                                .using(label=u"Waste"),

                CommonTopicsDict.named('resources_other') \
                                .using(label=u"Other - specify"),

                CommonTopicsDict.named('environment') \
                                .using(label=u"Environment and health"),
                
                CommonTopicsDict.named('air_pollution') \
                                .using(label=u"Air pollution & air quality"),

                CommonTopicsDict.named('water_pollution') \
                                .using(label=u"Water pollution & water quality"),

                CommonTopicsDict.named('noise_pollution') \
                                .using(label=u"Noise pollution"),

                CommonTopicsDict.named('environment_other') \
                                .using(label=u"Other - specify"),
        ),

        CommonDict.named('sectors') \
               .using(label=u"Sectors") \
               .of(

            CommonTopicsDict.named('agriculture') \
                            .using(label=u"Agriculture"),

            CommonTopicsDict.named('energy') \
                            .using(label=u"Energy"),

            CommonTopicsDict.named('transport') \
                            .using(label=u"Transport"),

            CommonTopicsDict.named('fisheries') \
                            .using(label=u"Fisheries"),

            CommonTopicsDict.named('forestry') \
                            .using(label=u"Forestry"),

            CommonTopicsDict.named('waste_management') \
                            .using(label=u"Waste management"),

            CommonTopicsDict.named('chemicals') \
                            .using(label=u"Chemicals/Industry (incl. mining)"),
        ),

        CommonDict.named('integration') \
               .using(label=u"Integration (with a separate focus)") \
               .of(

            CommonTopicsDict.named('links') \
                            .using(label=u"Links between topics and issues"),

            CommonTopicsDict.named('global') \
                            .using(label=u"Global dimension"),

            CommonTopicsDict.named('economic') \
                            .using(label=u"Economic dimension"),

            CommonTopicsDict.named('social') \
                            .using(label=u"Social dimension"),
        ),
    ),
)
