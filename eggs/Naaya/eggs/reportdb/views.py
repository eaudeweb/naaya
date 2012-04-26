import flask
import flatland.out.markup
import database
import schema
import file_upload
import datetime

from jinja2 import ChoiceLoader
from loader import ZopeTemplateLoader
from gtranslate import translate

class MarkupGenerator(flatland.out.markup.Generator):

    def __init__(self, template):
        super(MarkupGenerator, self).__init__("html")
        self.template = template

    def children_order(self, field):
        if isinstance(field, flatland.Mapping):
            return [kid.name for kid in field.field_schema]
        else:
            return []

    def widget(self, element, widget_name=None):
        if widget_name is None:
            widget_name = element.properties.get("widget", "input")
        widget_macro = getattr(self.template.module, widget_name)
        return widget_macro(self, element)


views = flask.Blueprint('views', __name__)


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


@views.route('/reports/new/', methods=['GET', 'POST'])
@views.route('/reports/<int:report_id>/edit/', methods=['GET', 'POST'])
def report_edit(report_id=None):
    if report_id is None:
        report_row = database.ReportRow()
        seris_review_row = database.SerisReviewRow()
    else:
        report_row = database.get_report_or_404(report_id)
        #TODO to be removed when there will be more than one seris
        seris_review_row = database.get_seris_reviews_list(report_id)[0]

    if flask.request.method == 'POST':
        session = database.get_session()
        form_data = {}
        form_data.update(schema.ReportSchema.from_defaults().flatten())
        form_data.update(schema.SerisReviewSchema.from_defaults().flatten())
        form_data.update(flask.request.form.to_dict())
        _expand_lists(form_data, ['header_country', 'format_lang_of_pub'])

        report_schema = schema.ReportSchema.from_flat(form_data)
        seris_review_schema = schema.SerisReviewSchema.from_flat(form_data)

        file_upload.handle_request(session, report_schema, report_row)
        if report_schema.validate():

            report_row.clear()
            report_row.update(report_schema.flatten())
            session.save(report_row)
            #TODO create filter to display data without losing information
            if report_row['format_availability_paper_or_web'] == 'paper only':
                report_row['format_availability_url'] = ''
            report_row['header_upload_date'] = datetime.datetime.now().strftime('%d %b %Y, %H:%M')
            session.save(report_row)
            seris_review_schema['report_id'].set(report_row.id)

            if seris_review_schema.validate():

                seris_review_row.clear()
                seris_review_row.update(seris_review_schema.flatten())
                if seris_review_row['structure_indicator_based'] == 'No':
                    seris_review_row['structure_indicators_estimation'] = ''
                if seris_review_row['structure_eea_indicators'] == 'No':
                    seris_review_row['structure_eea_indicators_estimated_no'] = ''
                if seris_review_row['structure_indicators_usage_to_evaluate'] == 'None':
                    seris_review_row['structure_indicators_usage_evaluation_method'] = ''
                session.save(seris_review_row)

                session.commit()
                flask.flash("Report saved.", "success")
                url = flask.url_for('views.seris_review_list',
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


@views.route('/reports/<int:report_id>/seris_reviews/')
def seris_review_list(report_id):
    app = flask.current_app
    report = database.get_report_or_404(report_id)
    return flask.render_template('seris_review_list.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-view.html')),
            'report': {'id': report_id,
                       'data': schema.ReportSchema.from_flat(report),
                       'seris_reviews': [
                          {'id': row.id,
                           'data': schema.SerisReviewSchema.from_flat(row)}
                          for row in database.get_seris_reviews_list(report_id,
                              debug=True)]
                      }
        }
    )


@views.route('/reports/<int:report_id>/seris_reviews/new/', methods=['GET', 'POST'])
@views.route('/reports/<int:report_id>/seris_reviews/<int:seris_review_id>/edit', 
             methods=['GET', 'POST'])
def seris_review_add(report_id, seris_review_id=None):
    if seris_review_id == None:
        seris_review_row = None
    else:
        seris_review_row = database.get_seris_or_404(seris_review_id)

    if flask.request.method == "GET":
        app = flask.current_app
        seris_review_schema = schema.SerisReviewSchema()
        if seris_review_id is not None:
            seris_review_schema['report_id'].set(report_id)
            seris_review_schema = schema.SerisReviewSchema \
                                        .from_flat(seris_review_row)
        return flask.render_template('seris_review_edit.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
            'report_id': report_id,
            'seris_review_schema': seris_review_schema,
        })

    session = database.get_session()
    form_data = dict(schema.SerisReviewSchema.from_defaults().flatten())
    form_data.update(flask.request.form.to_dict())
    seris_review_schema = schema.SerisReviewSchema.from_flat(form_data)
    # TODO validation
    if seris_review_row is None:
        seris_review_schema['report_id'].set(report_id)
        seris_review_row = database.SerisReviewRow()
    else:
        seris_review_schema['report_id'].set(seris_review_row['report_id'])
    seris_review_row.update(seris_review_schema.flatten())
    session.save(seris_review_row)
    session.commit()
    flask.flash("Review saved.", "success")
    return flask.redirect(flask.url_for('views.seris_review_list',
                                        report_id=report_id))


@views.route('/reports/<int:report_id>/seris_reviews/<int:seris_review_id>/')
def seris_review_view(report_id, seris_review_id):
    app = flask.current_app
    report = database.get_report_or_404(report_id)
    seris_review = database.get_seris_or_404(seris_review_id)
    return flask.render_template('seris_review_view.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-view.html')),
            'report': {'id': report_id,
                       'data': schema.ReportSchema.from_flat(report)},
            'seris': {'id': seris_review_id,
                       'data': schema.SerisReviewSchema.from_flat(seris_review),
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

    loaders = []
    if app.config["ZOPE_TEMPLATE_PATH"]:
        loaders.append(ZopeTemplateLoader(app.config["ZOPE_TEMPLATE_PATH"],
                                          app.config["ZOPE_TEMPLATE_CACHE"],
                                          app.config["ZOPE_TEMPLATE_LIST"]))
    loaders.append(app.create_global_jinja_loader())

    app.jinja_options = dict(app.jinja_options,
                             extensions=_my_extensions,
                             loader=ChoiceLoader(loaders))
