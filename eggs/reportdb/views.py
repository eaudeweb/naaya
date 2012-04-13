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


def register_on(app):
    app.register_blueprint(views)
