import flask
import database
import schema


views = flask.Blueprint('views', __name__)


@views.route('/')
def index():
    return "hello world!"


@views.route('/reports', methods=['GET'])
def report_list():
    return flask.render_template('report_list.html', **{
        'report_list': [{'id': row.id,
                         'data': schema.ReportSchema.from_flat(row).value}
                        for row in database.get_all_reports()],
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
    return "ok"


@views.route('/reports/<int:report_id>/seris_reviews', methods=['GET'])
def seris_review_list(report_id):
    return flask.render_template('seris_review_list.html', **{
        'review_list': [{'id': row.id,
                         'data': schema.SerisReviewSchema.from_flat(row).value}
                        for row in database.get_all_seris_reviews()],
    })


@views.route('/reports/<int:report_id>/seris_reviews', methods=['POST'])
def seris_review_add(report_id):
    session = database.get_session()
    seris_review_schema = schema.SerisReviewSchema.from_flat(
        flask.request.form.to_dict())
    seris_review_schema['report_id'].set(report_id)
    # TODO validation
    row = database.SerisReviewRow(seris_review_schema.flatten())
    session.save(row)
    session.commit()
    return "ok"


@views.route('/reports/<int:report_id>/seris_reviews/<int:seris_review_id>')
def seris_review_view(report_id, seris_review_id):
    return "hi"


def register_on(app):
    app.register_blueprint(views)
