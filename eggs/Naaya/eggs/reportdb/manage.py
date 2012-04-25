#!/usr/bin/env python

import flask
import flaskext.script


default_config = {
    'DATABASE_URI': 'postgresql://localhost/reportdb',
    'TESTING_DATABASE_URI': 'postgresql://localhost/reportdb_test',
    'ZOPE_TEMPLATE_CACHE': True,
    'ZOPE_TEMPLATE_PATH': None, #'http://forum.eionet.europa.eu/nrc-state-environment/report_templates/',
    'ZOPE_TEMPLATE_LIST': ['frame.html'],
}


def create_app():
    import views
    import database

    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.update(default_config)
    app.config.from_pyfile('settings.py', silent=True)

    _my_extensions = app.jinja_options["extensions"] + ["jinja2.ext.do"]
    app.jinja_options = dict(app.jinja_options, extensions=_my_extensions)

    database.initialize_app(app)
    views.register_on(app)

    return app


manager = flaskext.script.Manager(create_app)


@manager.command
def resetdb():
    import database
    database.get_session().drop_all()

@manager.command
def syncdb():
    import database
    database.get_session().create_all()


if __name__ == '__main__':
    import schema
    schema.register_handler_for_empty()
    manager.run()
