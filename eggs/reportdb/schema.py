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

        CommonEnum.named('frequency') \
                  .using(label=u"Frequency of publication") \
                  .valued(*sorted(publication_freq.keys())),
    ),

    CommonDict.named('format_section') \
              .using(label=u"FORMAT & ACCESSIBILITY") \
              .of(

        CommonEnum.named('format') \
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
topics_ratings = _load_json("refdata/topics_ratings.json")

CommonTopicsEnum = fl.Enum.using(optional=True) \
                          .with_properties(widget="radioselect") \
                          .valued(*sorted(topics_ratings.keys()))
CommonTopicsDict = CommonDict.of(

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

        fl.String.named("method_details") \
                .using(label=u"Details:"),
    ),

    CommonDict.named('topics') \
              .using(label=u"TOPICS COVERED") \
              .of(

        fl.Dict.named('media') \
               .with_properties(widget="schema") \
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

        fl.Dict.named('themes') \
               .with_properties(widget="schema") \
               .using(label=u"Environmental themes") \
               .of(

            CommonDict.named('climate_group') \
                      .using(label=u"Climate change") \
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
            ),
            
            CommonDict.named('nature_group') \
                      .using(label=u"Nature and biodiversity") \
                      .of(

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
            ),

            CommonDict.named('resources_group') \
                      .using(label=u"Natural resources and waste") \
                      .of(
                CommonTopicsDict.named('resources') \
                                .using(label=u"Natural resources and waste"),

                CommonTopicsDict.named('consumption') \
                                .using(label=u"Consumption/Urbanisation"),

                CommonTopicsDict.named('material_flow') \
                                .using(label=u"Material flow"),

                CommonTopicsDict.named('waste') \
                                .using(label=u"Waste"),

                CommonTopicsDict.named('other') \
                                .using(label=u"Other - specify"),
            ),

            CommonDict.named('environment_group') \
                      .using(label=u"Environment and health") \
                      .of(
                CommonTopicsDict.named('environment') \
                                .using(label=u"Environment and health"),
                
                CommonTopicsDict.named('air_pollution') \
                                .using(label=u"Air pollution & air quality"),

                CommonTopicsDict.named('water_pollution') \
                                .using(label=u"Water pollution & water quality"),

                CommonTopicsDict.named('noise_pollution') \
                                .using(label=u"Noise pollution"),

                CommonTopicsDict.named('other') \
                                .using(label=u"Other - specify"),
            ),
        ),

        fl.Dict.named('sectors') \
               .with_properties(widget="schema") \
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

        fl.Dict.named('integration') \
               .with_properties(widget="schema") \
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

        fl.Dict.named('fwd_info') \
               .with_properties(widget="schema") \
               .using(label=u"Forward-looking information") \
               .of(

            CommonDict.named('forecasts') \
                            .using(label=u"Forecasts & projections "
                                          "(post-report period)") \
                            .of(
                CommonTopicsEnum.named('focus') \
                          .using(label=u"Focus"),

                CommonTopicsEnum.named('indicators') \
                          .using(label=u"Indicators"),

                fl.String.named('no_of_indicators') \
                         .using(label=u"No. of indicators:"),
            ),

            CommonTopicsDict.named('global') \
                            .using(label=u"Global megatrends "
                                          "(not incl. global warming)"),

            CommonDict.named('multiple') \
                            .using(label=u"Multiple scenarios/futures") \
                            .of(
                CommonTopicsEnum.named('focus') \
                          .using(label=u"Focus"),

                CommonTopicsEnum.named('indicators') \
                          .using(label=u"Indicators"),

                fl.String.named('no_of_indicators') \
                         .using(label=u"Up to which year?"),
            ),
                            
            CommonTopicsDict.named('policy') \
                            .using(label=u"Policy recommendations"),
        )
    ),
)
