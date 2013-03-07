import datetime
from functools import wraps
import flask
import jinja2
import flatland.out.markup

import database
import schema
import file_upload
from gtranslate import translate
import frame
from schema import countries_list, regions_dict, subregions_dict

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


def edit_is_allowed():
    if flask.current_app.config.get('SKIP_EDIT_AUTHORIZATION', False):
        return True
    roles = getattr(flask.g, 'user_roles', [])
    return bool('Authenticated' in roles)


def require_edit_permission(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if edit_is_allowed():
            return func(*args, **kwargs)
        else:
            return "Please log in to access this view."
    return wrapper


@views.route('/')
def index():
    #TODO remove redirect when index will be implemented
    return flask.redirect(flask.url_for('views.report_list'))
    #return flask.render_template('index.html')


@views.route('/reports/')
def report_list():
    return flask.render_template('report_list.html', **{
        'report_list': [{'id': row.id,
                         'data': schema.ReportSchema.from_flat(row)}
                        for row in database.get_all_reports()],
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
    return flask.json.dumps(countries_list)

@views.route('/reports/new/get_subregions', methods=['GET'])
@views.route('/reports/<int:report_id>/edit/get_subregions', methods=['GET'])
def get_subregions(report_id=None):
    return flask.json.dumps(subregions_dict)

@views.route('/reports/new/', methods=['GET', 'POST'])
@views.route('/reports/<int:report_id>/edit/', methods=['GET', 'POST'])
@require_edit_permission
def report_edit(report_id=None):
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
        })


@views.route('/reports/<int:report_id>/delete/', methods=['POST'])
@require_edit_permission
def report_delete(report_id):
    if flask.request.method == 'POST':
        session = database.get_session()
        reviews_list = database.get_seris_reviews_list(report_id)
        if reviews_list:
            #TODO change when multiple reviews will be implemented
            session.table(database.SerisReviewRow) \
                   .delete(database.get_seris_reviews_list(report_id)[0].id)

        session.table(database.ReportRow).delete(report_id)
        session.commit()
        flask.flash("Report deleted.", "success")
        return flask.redirect(flask.url_for('views.report_list'))


@views.route('/reports/<int:report_id>/')
def report_view(report_id):
    app = flask.current_app
    report = database.get_report_or_404(report_id)
    return flask.render_template('report_view.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-view.html')),
            'report': {'id': report_id,
                       'data': schema.ReportSchema.from_flat(report),
                       'seris_reviews': [
                          {'id': row.id,
                           'data': schema.SerisReviewSchema.from_flat(row)}
                          for row in database.get_seris_reviews_list(report_id)]
                      }
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
