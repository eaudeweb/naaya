import flask
import htables

schema = htables.Schema()

ReportRow = schema.define_table('ReportRow', 'report')
SerisReviewRow = schema.define_table('SerisReviewRow', 'seris_review')


def get_report_or_404(report_id):
    try:
        return get_session().table(ReportRow).get(report_id)
    except KeyError:
        flask.abort(404)


def get_all_reports():
    return get_session().table(ReportRow).get_all()


def get_seris_or_404(seris_id):
    try:
        return get_session().table(SerisReviewRow).get(seris_id)
    except KeyError:
        flask.abort(404)


def get_seris_reviews_list(report_id):
    #TODO change when multiple reviews will be implemented
    all_reviews = get_all_seris_reviews()
    reviews_list = []
    for item in all_reviews:
        if item['report_id'] == str(report_id): reviews_list.append(item)
    return reviews_list

def get_seris_reviews_dict():
    #TODO change when multiple reviews will be implemented
    all_reviews = get_all_seris_reviews()
    reviews_dict = {}
    for item in all_reviews:
        reviews_dict[item['report_id']] = item
    return reviews_dict


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
