import flask
import htables


schema = htables.Schema()

ReportRow = schema.define_table('ReportRow', 'report')
SerisReviewRow = schema.define_table('SerisReviewRow', 'seris_review')


def get_all_reports():
    return get_session().table(ReportRow).get_all()


def get_all_seris_reviews():
    return get_session().table(SerisReviewRow).get_all()


def get_session():
    if not hasattr(flask.g, 'htables_session'):
        htables_pool = flask.current_app.extensions['htables_pool']
        flask.g.htables_session = htables_pool.get_session()
    return flask.g.htables_session


def initialize_app(app):
    connection_uri = app.config['DATABASE_URI']
    app.extensions['htables_pool'] = schema.bind(connection_uri, app.debug)

    @app.teardown_request
    def finalize_connection(response):
        session = getattr(flask.g, 'htables_session', None)
        if session is not None:
            app.extensions['htables_pool'].put_session(session)
            del flask.g.htables_session
