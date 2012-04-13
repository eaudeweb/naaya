import flask
import database


views = flask.Blueprint('views', __name__)


@views.route('/')
def index():
    return "hello world!"


@views.route('/reports', methods=['GET'])
def report_list():
    return flask.render_template('report_list.html', **{
        'report_row_list': list(database.get_all_reports()),
    })


@views.route('/reports', methods=['POST'])
def report_add():
    session = database.get_session()
    report_row = database.ReportRow({'title': flask.request.form['title']})
    session.save(report_row)
    session.commit()
    return "ok"


def register_on(app):
    app.register_blueprint(views)
