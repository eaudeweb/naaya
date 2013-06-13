import datetime
from functools import wraps
import flask
import jinja2
import flatland.out.markup
import flatland as fl
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
import database
import schema
import os
import json
import file_upload
from gtranslate import translate
import frame
from schema import countries_list, countries_dict, regions_dict, subregions_dict, check_common, mappings
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF, DCTERMS, SKOS, RDFS

def _load_json(name):
    with open(os.path.join(os.path.dirname(__file__), name), "rb") as f:
        return json.load(f)


eea_countries = _load_json("refdata/eea_countries.json")
cooperating_countries = _load_json("refdata/cooperating_countries.json")
processed_country_list = list(countries_list)

class MarkupGenerator(flatland.out.markup.Generator):

    def __init__(self, template):
        super(MarkupGenerator, self).__init__("html")
        self.template = template

    def children_order(self, field):
        if isinstance(field, flatland.Mapping):
            return [kid.name for kid in field.field_schema]
        else:
            return []

    def widget(self, element, widget_name=None, **kwargs):
        if widget_name is None:
            widget_name = element.properties.get("widget", "input")
        widget_macro = getattr(self.template.module, widget_name)
        return widget_macro(self, element, **kwargs)


views = flask.Blueprint('views', __name__)


views.before_request(frame.get_frame_before_request)

def edit_is_allowed(report_id=None):

    if flask.current_app.config.get('SKIP_EDIT_AUTHORIZATION', False):
        return True
    roles = getattr(flask.g, 'user_roles', [])
    if 'Administrator' in roles:
        return True
    groups = getattr(flask.g, 'groups', [])
    group_ids = [group[0] for group in groups]
    if check_common(schema.administrators, group_ids):
        return True
    if report_id is not None:
        report_row = database.get_report_or_404(report_id)
        for i in range(0, 40):
            country = report_row.get('header_country_%s' % i)
            if not country:
                break
            if not check_common(schema.countries_dict[country], group_ids):
                return False
        process_country_list(group_ids)
        return True
    else:
        if check_common(schema.all_contributors, group_ids):
            process_country_list(group_ids)
            return True


def process_country_list(group_ids):
    global processed_country_list
    processed_country_list = list(countries_list)
    for country in countries_list:
        for group_id in countries_dict[country]:
            if group_id in group_ids:
                break
        else:
            processed_country_list.remove(country)

def require_edit_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        report_id = kwargs.get('report_id')
        if edit_is_allowed(report_id):
            return func(*args, **kwargs)
        else:
            return flask.render_template('restricted.html', **{
                'user_id': getattr(flask.g, 'user_id')
            })
    return wrapper


@views.route('/')
def index():
    eea_countries_list = []
    cooperating_countries_list = []
    report_list = [schema.ReportSchema.from_flat(row)
                    for row in database.get_all_reports()]
    for country in eea_countries:
        count = 0
        for report in report_list:
            if country in report['header']['country'].value \
                    and len(report['header']['country'].value) == 1:
                count += 1
        eea_countries_list.append((country, count))
    for country in cooperating_countries:
        count = 0
        for report in report_list:
            if country in report['header']['country'].value \
                    and len(report['header']['country'].value) == 1:
                count += 1
        cooperating_countries_list.append((country, count))
    eea_count = 0
    for report in report_list:
        if 'European Environment Agency' in report['header']['region'].value:
            eea_count += 1
    return flask.render_template('index.html', **{
        'eea_countries_list': eea_countries_list,
        'cooperating_countries_list': cooperating_countries_list,
        'regions_list': [('European Environment Agency', eea_count)]
    })


@views.route('/reports/')
def report_list():
    report_list = [{
                    'id': row.id,
                    'extended_info': row['format_availability_paper_or_web'] and 'Yes' or 'No',
                    'data': schema.ReportSchema.from_flat(row)}
                        for row in database.get_all_reports()]
    country = flask.request.args.get('country')
    region = flask.request.args.get('region')
    if country:
        report_list = [report for report in report_list
            if country in report['data']['header']['country'].value
           and len(report['data']['header']['country'].value) == 1]
    if region:
        report_list = [report for report in report_list
            if region in report['data']['header']['region'].value]
    return flask.render_template('report_list.html', **{
        'report_list': report_list,
        'country': country,
        'region': region,
        'edit_is_allowed': edit_is_allowed(),
    })


def _expand_lists(form_data, keys):
    # TODO auto-detect the relevant fields in the schema
    for key in keys:
        form_data.pop(key, None)
        for (idx, value) in enumerate(flask.request.form.getlist(key)):
            form_data['%s_%d' % (key, idx)] = value


@views.route('/reports/new/get_regions', methods=['GET'])
@views.route('/reports/<int:report_id>/edit/get_regions', methods=['GET'])
def get_regions(report_id=None):
    return flask.json.dumps(regions_dict)

@views.route('/reports/new/get_countries', methods=['GET'])
@views.route('/reports/<int:report_id>/edit/get_countries', methods=['GET'])
def get_countries(report_id=None):
    return flask.json.dumps(processed_country_list)

@views.route('/reports/new/get_subregions', methods=['GET'])
@views.route('/reports/<int:report_id>/edit/get_subregions', methods=['GET'])
def get_subregions(report_id=None):
    return flask.json.dumps(subregions_dict)

@views.route('/reports/new/', methods=['GET', 'POST'])
@views.route('/reports/<int:report_id>/edit/', methods=['GET', 'POST'])
@require_edit_permission
def report_edit(report_id=None):
    country = flask.request.args.get('country')
    if not country:
        country = flask.request.form.get('country')
    if country == u'None':
        country = None
    region = flask.request.args.get('region')
    if not region:
        region = flask.request.form.get('region')
    if region == u'None':
        region = None
    if report_id is None:
        report_row = database.ReportRow()
        seris_review_row = database.SerisReviewRow()
    else:
        report_row = database.get_report_or_404(report_id)
        reviews_list = database.get_seris_reviews_list(report_id)
        if reviews_list:
            #TODO to be changed when there will be more than one seris
            seris_review_row = reviews_list[0]
        else:
            seris_review_row = database.SerisReviewRow()

    if flask.request.method == 'POST':
        session = database.get_session()
        form_data = {}
        form_data.update(schema.ReportSchema.from_defaults().flatten())
        form_data.update(schema.SerisReviewSchema.from_defaults().flatten())
        form_data.update(flask.request.form.to_dict())
        _expand_lists(form_data, ['header_region', 'header_country',
            'header_subregion', 'details_translated_in',
            'details_original_language', 'links_target_audience'])

        report_schema = schema.ReportSchema.from_flat(form_data)
        seris_review_schema = schema.SerisReviewSchema.from_flat(form_data)

        file_upload.handle_request(session, report_schema, report_row)
        if report_schema.validate():

            report_row.clear()
            report_row.update(report_schema.flatten())
            session.save(report_row)
            #TODO create filter to display data without losing information
            if report_row['format_report_type'] == 'report (static source)':
                report_row['format_date_of_last_update'] = ''
                report_row['format_freq_of_upd'] = ''
                report_row['format_size'] = ''
            if report_row['format_report_type'] == 'portals (dynamic source)':
                report_row['format_date_of_publication'] = ''
                report_row['format_freq_of_pub'] = ''
                report_row['format_no_of_pages'] = ''
            if report_row['format_availability_paper_or_web'] == 'paper only':
                report_row['format_availability_registration_required'] = ''
                report_row['format_availability_url'] = ''
            if report_row['format_availability_paper_or_web'] in [
                    'web only', 'web and print']:
                if not report_row['format_availability_registration_required']:
                    report_row['format_availability_costs'] = 'free'
            uploader = getattr(flask.g, 'user_id')
            if not uploader:
                uploader = 'Developer'
            report_row['header_uploader'] = uploader
            report_row['header_upload_date'] = datetime.datetime.now().strftime('%d %b %Y, %H:%M')
            session.save(report_row)
            seris_review_schema['report_id'].set(report_row.id)

            if seris_review_schema.validate():

                seris_review_row.clear()
                seris_review_row.update(seris_review_schema.flatten())
                if seris_review_row['structure_indicator_based'] == 'No':
                    seris_review_row['structure_indicators_estimation'] = ''
                    seris_review_row['structure_indicators_usage_to_compare_countries'] = ''
                    seris_review_row['structure_indicators_usage_to_compare_subnational'] = ''
                    seris_review_row['structure_indicators_usage_to_compare_eea'] = ''
                    seris_review_row['structure_indicators_usage_to_compare_global'] = ''
                    seris_review_row['structure_indicators_usage_to_assess_progress'] = ''
                    seris_review_row['structure_indicators_usage_to_evaluate'] = ''
                    seris_review_row['structure_indicators_usage_evaluation_method'] = ''
                elif not seris_review_row['structure_indicators_usage_to_evaluate']:
                    seris_review_row['structure_indicators_usage_evaluation_method'] = ''
                session.save(seris_review_row)

                session.commit()
                flask.flash("Report saved.", "success")
                url = flask.url_for('views.report_view',
                                    report_id=report_row.id)
                if country:
                    url = url+'?country='+country
                if region:
                    url = url+'?region='+region
                return flask.redirect(url)

        session.rollback()
        flask.flash("Errors in form.", "error")

    else:
        report_schema = schema.ReportSchema()
        seris_review_schema = schema.SerisReviewSchema()
        if report_id is not None:
            report_schema = schema.ReportSchema.from_flat(report_row)
            seris_review_schema = schema.SerisReviewSchema.from_flat(seris_review_row)

    app = flask.current_app
    return flask.render_template('report-edit.html', **{
        'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
        'report_id': report_id,
        'report_schema': report_schema,
        'seris_review_schema': seris_review_schema,
        'country': country,
        'region': region,
        })


@views.route('/rdf-mapping/', methods=['GET'])
def reports_rdf_mapping():
    return flask.jsonify(mappings)


@views.route('/rdf/', methods=['GET'])
def reports_rdf():
    g = Graph()
    count = [0]
    properties = {}
    get_schema_items(schema.ReportSchema(), properties, count)
    get_schema_items(schema.SerisReviewSchema(), properties, count)
    export = get_reports()

    bibo = Namespace('http://uri.gbv.de/ontology/bibo/')
    nao = Namespace('http://www.semanticdesktop.org/ontologies/2007/08/15/nao#')
    theme = Namespace('http://www.eea.europa.eu/themes/')
    bibtex = Namespace('http://purl.org/net/nknouf/ns/bibtex#')
    seris = Namespace('http://forum.eionet.europa.eu/nrc-state-environment/seris/ontology/schema.rdf#')
    mitype = Namespace('http://purl.org/dc/dcmitype/')

    for entry in export:
        current_id = entry['report_id']
        current_uri = "http://projects.eionet.europa.eu/seris-revision/seris/reports/%s" % current_id
        node = URIRef(current_uri)
        report = Namespace(current_uri)

        g.add((node, DCTERMS.type, mitype.Collection))
        g.add((node, DCTERMS.type, bibo.Document))
        g.add((node, DCTERMS.type, bibtex.Entry))
        g.add((node, DCTERMS.identifier, Literal(current_id)))

        for region in entry['header_region']:
            item = BNode()
            g.add((node, DCTERMS.spatial, item))
            g.add((item, DCTERMS.type, DCTERMS.Location))
            g.add((item, RDFS.label, Literal('Region of report')))
            g.add((item, DCTERMS.subject, Literal(region)))

        for country in entry['header_country']:
            g.add((node, DC.coverage, Literal(country)))

        if 'header_subregion' in entry.keys():
            for subregion in entry['header_subregion']:
                item = BNode()
                g.add((node, DCTERMS.spatial, item))
                g.add((item, DCTERMS.type, DCTERMS.Location))
                g.add((item, RDFS.label, Literal('Subregion of country')))
                g.add((item, DCTERMS.subject, Literal(subregion)))

        if entry['header_soer_cover']:
            g.add((node, DCTERMS.source, Literal(entry['header_soer_cover'])))

        if entry['details_original_name']:
            g.add((node, DC.title, Literal(entry['details_original_name'])))

        for lang in entry['details_original_language']:
            g.add((node, DC.language, Literal(lang)))

        if 'details_translated_in_0' in entry.keys():
            for lang in entry['details_translated_in_0']:
                item = BNode()
                g.add((node, DCTERMS.language, item))
                g.add((item, DCTERMS.type, DCTERMS.LinguisticSystem))
                g.add((
                    item,
                    RDFS.label,
                    Literal('Language in which the report was translated')))
                g.add((item, DCTERMS.subject, Literal(lang)))

        if entry['details_english_name']:
            g.add((
                  node,
                  DC.title,
                  Literal(entry['details_english_name'], lang="en")))

        if entry['details_publisher']:
            g.add((
                node,
                DC.publisher,
                Literal(entry['details_publisher'])))

        if entry['format_report_type']:
            g.add((node, DC.type, Literal(entry['format_report_type'])))

        if entry['format_date_of_publication']:
            g.add((
                node,
                DCTERMS.issued,
                Literal(entry['format_date_of_publication'])))

        if entry['format_freq_of_pub']:
            item = BNode()
            g.add((node, DCTERMS.accrualPeriodicity, item))
            g.add((item, DCTERMS.type, DCTERMS.Frequency))
            g.add((item, RDFS.label, Literal('Frequency of publication')))
            g.add((item, RDF.value, Literal(entry['format_freq_of_pub'])))

        if entry['format_date_of_last_update']:
            g.add((
                node,
                DCTERMS.modified,
                Literal(entry['format_date_of_last_update'])))

        if entry['format_freq_of_upd']:
            item = BNode()
            g.add((node, DCTERMS.accrualPeriodicity, item))
            g.add((item, DCTERMS.type, DCTERMS.Frequency))
            g.add((item, RDFS.label, Literal('Frequency of update')))
            g.add((item, RDF.value, Literal(entry['format_freq_of_upd'])))

        if entry['format_no_of_pages']:
            g.add((node, bibo.numpages, Literal(entry['format_no_of_pages'])))

        if entry['format_size']:
            item = BNode()
            g.add((node, DCTERMS.extent, item))
            g.add((item, DCTERMS.type, DCTERMS.SizeOrDuration))
            g.add((item, RDFS.label, Literal('Size in MBytes')))
            g.add((item, RDF.value, Literal(entry['format_size'])))

        if entry['format_availability_paper_or_web']:
            g.add((
                node,
                DC['format'],
                Literal(entry['format_availability_paper_or_web'])))

        if entry['format_availability_url']:
            g.add((
                node,
                bibtex.hasURL,
                Literal(entry['format_availability_url'])))

        if entry['format_availability_registration_required']:
            g.add((
                node,
                DC.rights,
                Literal(entry['format_availability_registration_required'])))

        if entry['format_availability_costs']:
            g.add((
                node,
                RDFS.comment,
                Literal('(cost)' + entry['format_availability_costs'])))

        if 'links_target_audience' in entry.keys():
            for audience in entry['links_target_audience']:
                item = BNode()
                g.add((node, DCTERMS.audience, item))
                g.add((item, DCTERMS.type, DCTERMS.AgentClass))
                g.add((item, RDFS.label, Literal('Target audience')))
                g.add((item, RDF.value, Literal(audience)))

        if entry['links_legal_reference']:
            item = BNode()
            g.add((node, DCTERMS.conformTo, item))
            g.add((item, DCTERMS.type, DCTERMS.Standard))
            g.add((item, RDFS.label, Literal('Legal reference')))
            g.add((item, RDF.value, Literal(entry['links_legal_reference'])))

        if entry['links_explanatory_text']:
            g.add((
                node,
                bibo.shortDescription,
                Literal(entry['links_explanatory_text'])))

        topics = { "env_issues": ['air',
                                  'biodiversity',
                                  'chemicals',
                                  'climate',
                                  'human',
                                  'landuse',
                                  'natural',
                                  'noise',
                                  'soil',
                                  'waste',
                                  'water',
                                  'other_issues'],
                  'sectors_and_activities' : ['agriculture',
                                              'energy',
                                              'fishery',
                                              'households',
                                              'industry',
                                              'economy',
                                              'tourism',
                                              'transport'],
                  'across_env': ['technology',
                                 'policy',
                                 'scenarios'],
                  'env_regions': ['coast_sea',
                                  'regions',
                                  'urban']}

        for key in topics.keys():
            for topic in topics[key]:
                focus = 'topics_' + key + '_' + topic + '_focus'
                indicators = 'topics_' + key + '_' + topic + '_indicators'
                current_item = "http://www.eea.europa.eu/themes/%(topic)s" % {"topic": topic}
                item = BNode()
                if (entry[focus] or entry[indicators]):
                    g.add((node, nao.hasTopic, item))
                    g.add((item, RDFS.label, Literal(topic)))
                    g.add((item, DCTERMS.type, bibtex.Entry))
                    g.add((item, bibtex.hasURL, Literal(current_item)))
                    if entry[focus]:
                        g.add((
                            item,
                            seris.hasFocusValue,
                            Literal(entry[focus])))
                    if entry[indicators]:
                        g.add((
                            item,
                            seris.hasIndicatorCount,
                            Literal(entry[indicators])))
            topic = 'topics_' + key + '_extra_topic_extra_topic_input'
            focus = 'topics_' + key + '_extra_topic_other_radio_focus'
            indicators = 'topics_' + key + '_extra_topic_other_radio_indicators'
            if entry[topic]:
                item = BNode()
                g.add((node, nao.hasTopic, item))
                g.add((item, RDFS.label, Literal(entry[topic])))
                g.add((item, DCTERMS.type, bibtex.Entry))
                if entry[focus]:
                    g.add((
                        item,
                        seris.hasFocusValue,
                        Literal(entry[focus])))
                if entry[indicators]:
                    g.add((
                        item,
                        seris.hasIndicatorCount,
                        Literal(entry[indicators])))

        if entry['structure_indicator_based']:
            item = BNode()
            g.add((node, seris.structure, item))
            g.add((item, RDFS.label, Literal('indicator based')))
            if entry['structure_indicators_estimation']:
                g.add((
                    item,
                    RDF.value,
                    Literal(entry['structure_indicators_estimation'])))
            usage = ''
            if entry['structure_indicators_usage_to_assess_progress']:
                usage += entry['structure_indicators_usage_to_assess_progress']
                usage += ' to assess progress to target/treshold.'
            if entry['structure_indicators_usage_to_compare_countries']:
                usage += entry['structure_indicators_usage_to_compare_countries']
                usage += ' to compare with other countries/EU.'
            if entry['structure_indicators_usage_to_compare_subnational']:
                usage += entry['structure_indicators_usage_to_compare_subnational']
                usage += ' to compare at subnational level.'
            if entry['structure_indicators_usage_to_compare_eea']:
                usage += entry['structure_indicators_usage_to_compare_eea']
                usage += ' to relate with EEA/EU developments.'
            if entry['structure_indicators_usage_to_compare_global']:
                usage += entry['structure_indicators_usage_to_compare_global']
                usage += ' to relate to global developments.'
            if entry['structure_indicators_usage_to_evaluate']:
                usage += entry['structure_indicators_usage_to_evaluate']
                usage += ' to rank/evaluate.'
                if entry['structure_indicators_usage_evaluation_method']:
                    usage += 'evaluation method: '
                    usage += entry['structure_indicators_usage_evaluation_method']
            if usage:
                g.add((item, SKOS.scopeNote, Literal(usage)))

        if entry['structure_policy_recommendations']:
            g.add((
                node,
                seris.policyRecommendationsQuantifier,
                Literal(entry['structure_policy_recommendations'])))

        if entry['structure_reference']:
            quantifier = entry['structure_reference']
            if quantifier[0] == 'N':
                quantifier = 'No'

            text = '[%s] DPSIR framework used' % quantifier
            g.add((node, DCTERMS.references, Literal(text)))

        if entry['short_description']:
            g.add((
                node,
                DCTERMS.description,
                Literal(entry['short_description'])))

        if entry['table_of_contents']:
            g.add((
                node,
                DCTERMS.tableOfContents,
                Literal(entry['table_of_contents'])))

    g.bind("dcterms", DCTERMS)
    g.bind("dc", DC)
    g.bind("bibo", bibo)
    g.bind("foaf", FOAF)
    g.bind("nao", nao)
    g.bind("theme", theme)
    g.bind("report", report)
    g.bind("bibtex", bibtex)
    g.bind("skos", SKOS)
    g.bind("rdfs", RDFS)
    g.bind("seris", seris)

    return flask.Response(g.serialize(format='xml'), mimetype='text/xml')


@views.route('/atom/', methods=['GET'])
def reports_atom():
    from datetime import datetime
    #TODO change when multiple reviews will be implemented
    feed = AtomFeed('SERIS Reports',
                    feed_url=make_external('atom'),
                    url=make_external('')
                    )
    for report in get_reports(with_url=True):
        feed.add(report['details_original_name'],
                 unicode(report['short_description']),
                 content_type='html', author=report['header_uploader'],
                 url=make_external(report['url']),
                 updated=datetime.strptime(report['header_upload_date'],
                        '%d %b %Y, %H:%M'))
    return feed.get_response()

@views.route('/json/', methods=['GET'])
def reports_json():
    #TODO change when multiple reviews will be implemented
    export = {}
    properties = {}
    count = [0]
    get_schema_items(schema.ReportSchema(), properties, count)
    get_schema_items(schema.SerisReviewSchema(), properties, count)
    export['items'] = get_reports()
    export['properties'] = properties
    return flask.jsonify(export)

def make_external(url):
    return urljoin(flask.request.url_root, url)
    #return urljoin('http://projects.eionet.europa.eu/seris-revision/seris', url)

def get_reports(with_url=None):
    reports = []
    reviews_dict = database.get_seris_reviews_dict()
    for report in database.get_all_reports():
        header_country = []
        header_region = []
        details_original_language = []
        for i in range(0, 50):
            country = report.get('header_country_%s' % i)
            if country:
                header_country.append(country)
                del(report['header_country_%s' % i])
            region = report.get('header_region_%s' % i)
            if region:
                header_region.append(region)
                del(report['header_region_%s' % i])
            language = report.get('details_original_language_%s' % i)
            if language:
                details_original_language.append(language)
                del(report['details_original_language_%s' % i])
        report['header_country'] = header_country
        report['header_region'] = header_region
        report['details_original_language'] = details_original_language
        if with_url:
            report['url'] = make_external(flask.url_for('views.report_view',
                            report_id=report.id))
        seris_review = reviews_dict[str(report.id)]
        reports.append(dict(report, **seris_review))
    return reports


def get_schema_items(ob, properties, count):
    if hasattr(ob, 'field_schema'):
        for child_schema in ob.field_schema:
            child = ob[child_schema.name]
            get_schema_items(child, properties, count)
    else:
        if isinstance(ob, fl.List):
            valueType = 'list'
        elif isinstance(ob, fl.String):
            valueType = 'text'
        elif isinstance(ob, fl.Integer):
            valueType = 'integer'
        elif isinstance(ob, fl.Enum):
            valueType = 'text'
        elif isinstance(ob, fl.Boolean):
            valueType = 'bool'
        properties[ob.flattened_name()] = {'valueType': valueType, 'order': count[0]}
        count[0] += 1

@views.route('/reports/<int:report_id>/delete/', methods=['POST'])
@require_edit_permission
def report_delete(report_id):
    if flask.request.method == 'POST':
        session = database.get_session()
        reviews_list = database.get_seris_reviews_list(report_id)
        if reviews_list:
            #TODO change when multiple reviews will be implemented
            session.table(database.SerisReviewRow) \
                   .delete(reviews_list[0].id)

        session.table(database.ReportRow).delete(report_id)
        session.commit()
        flask.flash("Report deleted.", "success")
        url = flask.url_for('views.report_list')
        country = flask.request.args.get('country')
        if country:
            url = url+'?country='+country
        region = flask.request.args.get('region')
        if region:
            url = url+'?region='+region
        return flask.redirect(url)


@views.route('/reports/<int:report_id>/')
def report_view(report_id):
    app = flask.current_app
    report = database.get_report_or_404(report_id)
    country = flask.request.args.get('country')
    region = flask.request.args.get('region')
    return flask.render_template('report_view.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-view.html')),
            'report': {'id': report_id,
                       'data': schema.ReportSchema.from_flat(report),
                       'seris_reviews': [
                          {'id': row.id,
                           'data': schema.SerisReviewSchema.from_flat(row)}
                          for row in database.get_seris_reviews_list(report_id)]
                      },
            'country': country,
            'region': region,
            'edit_is_allowed': edit_is_allowed(),
        }
    )


@views.route('/translate', methods=['GET', 'POST'])
def google_translate():
    text = flask.request.args.get('text')
    dest_lang = flask.request.args.get('dest_lang')
    src_lang = flask.request.args.get('src_lang')
    return translate(text, dest_lang, src_lang)

@views.route('/download/<int:db_id>')
def download(db_id):
    session = database.get_session()
    try:
        db_file = session.get_db_file(db_id)
    except KeyError:
        flask.abort(404)
    return flask.Response(''.join(db_file.iter_data()), # TODO stream response
                          mimetype="application/octet-stream")


def register_on(app):
    app.register_blueprint(views)
    _my_extensions = app.jinja_options['extensions'] + ['jinja2.ext.do']
    template_loader = jinja2.ChoiceLoader([
        frame.FrameTemplateLoader(),
        app.create_global_jinja_loader(),
    ])

    app.jinja_options = dict(app.jinja_options,
                             extensions=_my_extensions,
                             loader=template_loader)
