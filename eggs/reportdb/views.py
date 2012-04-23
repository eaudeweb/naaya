import flask
import flatland.out.markup
import database
import schema

from jinja2 import ChoiceLoader
from loader import ZopeTemplateLoader

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
                         'data': schema.ReportSchema.from_flat(row).value}
                        for row in database.get_all_reports()],
    })

"""
@views.route('/reports/new/')
@views.route('/reports/<int:report_id>/edit/')
def report_edit(report_id=None):
    app = flask.current_app
    report_schema = schema.ReportSchema()
    seris_review_schema = schema.SerisReviewSchema()
    return flask.render_template('report-edit.html', **{
        'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
        'report_id': report_id,
        'report_schema': report_schema,
        'seris_review_schema': seris_review_schema,
    })
"""

@views.route('/reports/new/', methods=['GET', 'POST'])
@views.route('/reports/<int:report_id>/edit/', methods=['GET', 'POST'])
def report_edit(report_id=None):
    if report_id == None:
        report_row = None
    else:
        report_row = database.get_report_or_404(report_id)

    if flask.request.method == 'GET':
        app = flask.current_app
        report_schema = schema.ReportSchema()
        seris_review_schema = schema.SerisReviewSchema()
        return flask.render_template('report-edit.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
            'report_id': report_id,
            'report_schema': report_schema,
            'seris_review_schema': seris_review_schema,
            })

    session = database.get_session()
    form_data = dict(schema.ReportSchema())
    form_data.update(flask.request.form.to_dict())
    report_schema = schema.ReportSchema.from_flat(form_data)
    # TODO validation
    if report_row is None:
        report_row = database.ReportRow()
    report_row.update(report_schema.flatten())
    session.save(report_row)
    session.commit()
    flask.flash("Report saved", "success")
    seris_review_schema = schema.SerisReviewSchema.from_flat(
                                    flask.request.form.to_dict())
    seris_review_schema['report_id'].set(report_row.id)
    seris_review_row = database.SerisReviewRow(seris_review_schema.flatten())
    session.save(seris_review_row)
    session.commit()
    return flask.redirect(flask.url_for('views.report_list'))


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
                           'data': schema.SerisReviewSchema.from_flat(row).value}
                          for row in database.get_seris_reviews_list(report_id)]
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
        if seris_review_id != None:
            seris_review_schema['report_id'].set(report_id)
            seris_review_schema = schema.SerisReviewSchema \
                                        .from_flat(seris_review_row)
        return flask.render_template('seris_review_edit.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
            'report_id': report_id,
            'seris_review_schema': seris_review_schema,
        })

    session = database.get_session()
    form_data = dict(schema.SerisReviewSchema())
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
