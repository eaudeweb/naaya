from webob.dec import wsgify
from wsgiref.simple_server import make_server

@wsgify.middleware
def no_hop_by_hop(request, app):
    """ remove the Connection hop-by-hop header """
    response = request.get_response(app)
    del response.headers['Connection']
    return response

def create_user(db, user_id, password):
    import transaction
    app = db.open().root()['Application']
    app.acl_users._doAddUser('admin', 'admin', ['Manager'], [])
    transaction.commit()

def demo_http_server(tzope):
    state = {'flush_db': False}

    @wsgify.middleware
    def flush_db_middleware(request, app):
        if request.path_info.endswith('/__flush'):
            state['flush_db'] = True
        return app

    create_user(tzope.orig_db, 'admin', 'admin')

    app = flush_db_middleware(tzope.wsgi_app)
    httpd = make_server('127.0.0.1', 8080, no_hop_by_hop(app))

    while True:
        _cleanup_db_layer, db_layer = tzope.db_layer()
        try:
            print "waiting for requests. Go to /__flush to reload the db."
            while not state['flush_db']:
                httpd.handle_request()
            state['flush_db'] = False

        finally:
            _cleanup_db_layer()
