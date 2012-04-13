import flask


views = flask.Blueprint('views', __name__)


@views.route('/')
def index():
    return "hello world!"


def register_on(app):
    app.register_blueprint(views)
