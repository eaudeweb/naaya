import flatland as fl
import flask
import os
import json
import database
import datetime
from flatland.validation import Validator, Converted, Present
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
RegistrationBoolean = fl.Boolean.with_properties(widget="registration_checkbox")

update_years = publication_years = [str(year) for year in xrange(1990,
                                           datetime.datetime.now().year+1)]
publication_freq = _load_json("refdata/publication_freq.json")
update_freq = _load_json("refdata/update_freq.json")
regions_dict = _load_json("refdata/regions_list.json")
regions_list = regions_dict.keys()
subregions_dict = _load_json("refdata/subregions_list.json")
subregions_list = []
for country in subregions_dict.keys():
    subregions_list += subregions_dict[country]
countries_data = _load_json("refdata/countries_list.json")
countries_dict = {}
countries_list = []
all_contributors = []
for country_data in countries_data:
    countries_list.append(country_data[0])
    all_contributors.extend(country_data[1])
    countries_dict[country_data[0]] = country_data[1]
administrators = _load_json("refdata/administrators.json")
target_audience = _load_json("refdata/target_audience.json")
languages = _load_json("refdata/languages_list.json")
language_codes = [pair[1] for pair in
                  sorted([(v,k) for (k,v) in languages.items()])]

indicators_estimation = _load_json("refdata/indicators_estimation.json")
mappings = _load_json("refdata/rdf_mappings.json")

class IsInteger(Validator):

    fail = None

    def validate(self, element, state):
        if element.properties.get("not_empty_error"):
            self.fail = fl.validation.base.N_(element.properties["not_empty_error"])
        else:
            self.fail = fl.validation.base.N_(u'%(u)s is not a valid value for %(label)s.')

        if not isinstance(element.value, int):
            return self.note_error(element, state, 'fail')

        return True


class AccessibleCountries(Validator):

    fail = None

    def validate(self, element, state):
        if flask.current_app.config.get('SKIP_EDIT_AUTHORIZATION', False):
            return True
        user_id = getattr(flask.g, 'user_id', '')
        groups = getattr(flask.g, 'groups', [])
        group_ids = [group[0] for group in groups]
        accessible_countries = []
        roles = getattr(flask.g, 'user_roles', [])
        for country in countries_list:
            if check_common(countries_dict[country], group_ids):
                accessible_countries.append(country)
        if element.value == []:
            element.errors.append('%s field is mandatory' % (element.label))
            return False
        if not (set(element.value).issubset(set(accessible_countries))
                or 'Administrator' in roles):
            element.errors.append("User %s has access only for: %s" %
                (user_id, (', ').join(accessible_countries)))
            return False

        return True

def check_common(needed_rights, existing_rights):
    return not set(needed_rights).isdisjoint(set(existing_rights))

ReportSchema = fl.Dict.with_properties(widget="schema") \
                      .of(

    CommonDict.named('header') \
              .using(label=u"") \
              .of(

        fl.List.named('region') \
               .using(label=u"Region", optional=True) \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                placeholder="Select region(s)...",
                                field_type='hidden') \
               .of(

            CommonEnum.valued(*regions_list)

        ),

        fl.List.named('country') \
               .using(label=u"Country") \
               .including_validators(AccessibleCountries()) \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                placeholder="Select countries ...") \
               .of(

            CommonEnum.valued(*countries_list)

        ),

        fl.List.named('subregion') \
               .using(label=u"Sub-national", optional=True) \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                placeholder="Select sub-regions ...") \
               .of(

            CommonEnum.valued(*subregions_list)

        ),

        CommonFile.named('soer_cover') \
                  .using(label=u"Copy of SOER cover") \
                  .with_properties(widget_image=True),

        CommonString.named('uploader') \
                    .with_properties(field_type='hidden') \
                    .using(label=u"Factsheet prepared by"),

        CommonString.named('upload_date') \
                    .with_properties(field_type='hidden') \
                    .using(label=u"Latest update")

    ),

    CommonDict.named('details') \
              .using(label=u"REPORT DETAILS") \
              .of(

        CommonString.named('original_name') \
                    .using(label=u"Title - in original language",
                           optional=False)
                    .with_properties(css_class="input-big"),

        fl.List.named('original_language') \
                  .using(label=u"Original Language(s)") \
                  .with_properties(widget="multiple_select",
                                   placeholder="Select a language ...",
                                   widget_chosen=True) \
                  .of(

              CommonEnum.valued(*language_codes) \
                      .with_properties(value_labels=languages)
        ),

        fl.List.named('translated_in') \
               .using(label=u"Translated in following languages",
               optional=True) \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                placeholder="Select languages ...") \
               .of(

            CommonEnum.valued(*language_codes) \
                      .with_properties(value_labels=languages)

        ),

        CommonString.named('english_name') \
                    .using(label=u"Title (in English)") \
                    .with_properties(css_class="input-big"),

        CommonString.named('publisher') \
                    .using(label=u"Published by") \
                    .with_properties(css_class="input-medium"),

    ),

    CommonDict.named('format') \
              .using(label=u"FORMAT & ACCESSIBILITY") \
              .of(

        fl.Enum.named('report_type') \
               .with_properties(widget="radioselect") \
               .valued(*(["report (static source)", "portal (dynamic source)"])) \
               .using(label=u"Report type"),

        CommonEnum.named('date_of_publication') \
                    .using(label=u"Year of publication") \
                    .valued(*publication_years) \
                    .with_properties(css_class="select-small static-source",
                                     hide_if_empty='True'),

        CommonEnum.named('date_of_last_update') \
                    .using(label=u"Year of last update") \
                    .valued(*update_years) \
                    .with_properties(css_class="select-small dynamic-source",
                                     hide_if_empty='True'),

        CommonEnum.named('freq_of_pub') \
                  .using(label=u"Frequency of publication") \
                  .valued(*publication_freq) \
                  .with_properties(css_class="select-small static-source",
                                   hide_if_empty='True'),

        CommonEnum.named('freq_of_upd') \
                  .using(label=u"Frequency of updates") \
                  .valued(*update_freq) \
                  .with_properties(css_class="select-small dynamic-source",
                                   hide_if_empty='True'),

        fl.Integer.named('no_of_pages') \
                  .using(label=u"No. of pages",
                         optional=True) \
                  .including_validators(IsInteger()) \
                  .with_properties(css_class="input-small static-source",
                                   hide_if_empty='True'),

        fl.Integer.named('size') \
                  .using(label=u"Size (MBytes)",
                         optional=True) \
                  .including_validators(IsInteger()) \
                  .with_properties(css_class="input-small dynamic-source",
                                   hide_if_empty='True'),

        fl.Dict.named('availability') \
               .with_properties(widget="availability_section") \
               .using(label=u"Availability")\
               .of(

            fl.Enum.named('paper_or_web') \
                   .with_properties(widget="radioselect", hide_if_empty='True') \
                   .valued(*(["paper only", "web only", "web and print"])) \
                   .using(label=u""),

            CommonString.named("url") \
                        .with_properties(widget="url") \
                        .using(label=u"URL"),

            RegistrationBoolean.named('registration_required') \
                   .using(label=u"registration required"),

            fl.Enum.named('costs') \
                   .with_properties(widget="radioselect", hide_if_empty='True') \
                   .valued(*(["free", "with costs"])) \
                   .using(label=u""),

        ),

    ),

    CommonDict.named('links') \
              .using(label=u"AUDIENCE & CONTEXT") \
              .of(

        fl.List.named('target_audience') \
               .using(label=u"Target audience", optional=True) \
               .with_properties(widget="multiple_select",
                                widget_chosen=True,
                                placeholder="Select target audience(s)...") \
               .of(

            CommonEnum.valued(*target_audience)

        ),

        CommonString.named('legal_reference') \
                    .using(label=u"Legal reference") \
                    .with_properties(widget="textarea",
                                     hide_if_empty='True'),

        CommonString.named("explanatory_text") \
                    .using(label=u"Further information (if applicable)") \
                    .with_properties(widget="textarea",
                                     hide_if_empty='True'),

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

    fl.Integer.named('report_id')
              .with_properties(field_type='hidden') \
              .using(label="Report id"),

    CommonDict.named('structure') \
              .using(label=u"STRUCTURE") \
              .of(

        fl.Enum.named('indicator_based') \
               .with_properties(widget="radioselect") \
               .valued(*(["Yes", "No"])) \
               .using(label=u"Indicator based assessment",
                         optional=True),

        CommonEnum.named('indicators_estimation') \
                  .valued(*indicators_estimation) \
                  .with_properties(hide_if_empty='True') \
                  .using(label=u"Number of indicators"),

        fl.Dict.named('indicators_usage') \
               .using(label=u"How are indicators used") \
               .with_properties(widget="indicators_group", hidden_label="True") \
               .of(

            IndicatorEnum.named('to_assess_progress') \
                         .valued(*indicators_usage) \
                         .using(label=u"To asses progress to target/threshold"),

            IndicatorEnum.named('to_compare_countries') \
                         .valued(*indicators_usage) \
                         .using(label=u"To compare with other countries/EU"),

            IndicatorEnum.named('to_compare_subnational') \
                         .valued(*indicators_usage) \
                         .using(label=u"To compare at sub-national level"),

            IndicatorEnum.named('to_compare_eea') \
                         .valued(*indicators_usage) \
                         .using(label=u"To relate with EEA/EU developments"),

            IndicatorEnum.named('to_compare_global') \
                         .valued(*indicators_usage) \
                         .using(label=u"To relate to global developments"),

            IndicatorEnum.named('to_evaluate') \
                         .valued(*indicators_usage) \
                         .using(label=u"To rank/evaluate (e.g. with 'smileys')"),

            CommonEnum.named("evaluation_method") \
                      .valued(*evaluation_methods) \
                      .using(label=u"If yes, how"),
        ),

        fl.Enum.named('policy_recommendations') \
               .with_properties(widget="radioselect") \
               .valued(*(["Explicitly", "Implicitly", "None"])) \
               .using(label=u"Report gives policy recommendations"),

        fl.Enum.named('reference') \
               .with_properties(widget="radioselect") \
               .valued(*(["Explicitly", "Implicitly", "Not used"])) \
               .using(label=u"DPSIR framework used"),

    ),

    fl.Dict.named('topics') \
           .using(label=u"TOPICS COVERED") \
           .with_properties(widget="topics_group") \
           .of(

        fl.Dict.named('env_issues') \
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

        fl.Dict.named('sectors_and_activities') \
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

        fl.Dict.named('across_env') \
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

        fl.Dict.named('env_regions') \
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

    ),

    CommonString.named("short_description") \
                .using(label=u"Short description from SERIS (old):") \
                .with_properties(widget="textarea",
                                 hide_if_empty='True'),

    CommonString.named("table_of_contents") \
                .using(label=u"Overview of table of contents and "
                              "indicators in report") \
                .with_properties(widget="textarea",
                                 hide_if_empty='True'),

)
