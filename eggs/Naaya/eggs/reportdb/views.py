import flask
import flatland.out.markup
import database
import schema


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


@views.route('/reports')
def report_list():
    return flask.render_template('report_list.html', **{
        'report_list': [{'id': row.id,
                         'data': schema.ReportSchema.from_flat(row).value}
                        for row in database.get_all_reports()],
    })


@views.route('/reports/new')
def report_edit():
    app = flask.current_app
    report_schema = schema.ReportSchema()
    return flask.render_template('report-edit.html', **{
        'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
        'report_schema': report_schema,
    })


@views.route('/reports', methods=['POST'])
def report_add():
    session = database.get_session()
    request_data = flask.request.form.to_dict()
    report_schema = schema.ReportSchema.from_flat(request_data)
    # TODO validation
    row = database.ReportRow(report_schema.flatten())
    session.save(row)
    session.commit()
    return flask.redirect(flask.url_for('views.report_list'))


@views.route('/reports/<int:report_id>/seris_reviews')
def seris_review_list(report_id):
    report = database.get_report_or_404(report_id)
    return flask.render_template('seris_review_list.html', 
        **{'report': {'id': report_id,
                      'data': schema.ReportSchema.from_flat(report),
                      'seris_reviews': [{'id': row.id,
                                         'data': schema.SerisReviewSchema.from_flat(row).value}
                                       for row in database.get_all_seris_reviews()]}
        }
    )


@views.route('/reports/<int:report_id>/seris_reviews/new', methods=['GET', 'POST'])
def seris_review_add(report_id):
    if flask.request.method == "GET":
        app = flask.current_app
        seris_review_schema = schema.SerisReviewSchema()
        seris_review_schema['report_id'].set(report_id)
        return flask.render_template('seris_review_edit.html', **{
            'mk': MarkupGenerator(app.jinja_env.get_template('widgets-edit.html')),
            'seris_review_schema': seris_review_schema,
        })

    session = database.get_session()
    seris_review_schema = schema.SerisReviewSchema.from_flat(
        flask.request.form.to_dict())
    seris_review_schema['report_id'].set(report_id)
    # TODO validation
    row = database.SerisReviewRow(seris_review_schema.flatten())
    session.save(row)
    session.commit()
    return flask.redirect(flask.url_for('views.seris_review_list',
        report_id=report_id))


@views.route('/reports/<int:report_id>/seris_reviews/<int:seris_review_id>')
def seris_review_view(report_id, seris_review_id):
    return "This is review: "+str(report_id)+'.'+str(seris_review_id)


def register_on(app):
    app.register_blueprint(views)
