"""
Zope 5 test environment wrapper for naaya-nose.

Boots a Zope 5 WSGI application without starting an HTTP server,
then wraps the database in DemoStorage for test isolation.
"""
import sys
import os
from tempfile import mkstemp

import ZODB.DB
from ZODB.DemoStorage import DemoStorage


def wsgi_publish(environ, start_response):
    """WSGI app that delegates to Zope's publish_module."""
    from ZPublisher.WSGIPublisher import publish_module
    return publish_module(environ, start_response)


def conf_for_test(zope_conf_path):
    """Create a temporary zope.conf with MappingStorage for tests."""
    newline = '\r\n' if sys.platform == 'win32' else '\n'
    start_marker = '<zodb_db main>' + newline
    end_marker = '</zodb_db>' + newline
    new_text = ('    <mappingstorage>' + newline +
                '    </mappingstorage>' + newline +
                '    mount-point /' + newline)

    with open(zope_conf_path, 'r') as f:
        orig_cfg = f.read()

    start_idx = orig_cfg.index(start_marker) + len(start_marker)
    end_idx = orig_cfg.index(end_marker)
    new_cfg = orig_cfg[:start_idx] + new_text + orig_cfg[end_idx:]

    fd, conf_path = mkstemp(suffix='.conf')
    with os.fdopen(fd, 'w') as config_file:
        config_file.write(new_cfg)

    def cleanup():
        os.unlink(conf_path)

    return cleanup, conf_path


def zope_startup(orig_conf_path, nodemo=False):
    """Boot Zope 5 from a config file without starting HTTP servers."""
    import Zope2

    if not nodemo:
        _cleanup_conf, conf_path = conf_for_test(orig_conf_path)
    else:
        _cleanup_conf, conf_path = None, orig_conf_path

    try:
        # Zope 5 startup: configure + make_wsgi_app
        from Zope2.Startup.run import configure_wsgi
        configure_wsgi(conf_path)
        app = Zope2.app()
        app._p_jar.close()
    finally:
        if callable(_cleanup_conf):
            _cleanup_conf()

    orig_db = Zope2.bobo_application._db

    def db_layer():
        """Create a DemoStorage that wraps the original storage."""
        base_db = Zope2.bobo_application._db

        demo_storage = DemoStorage(base=base_db.storage)

        # Remove from databases dict to avoid duplicate name error
        base_db.databases.pop(base_db.database_name, None)

        wrapper_db = ZODB.DB(storage=demo_storage,
                             database_name=base_db.database_name,
                             databases=base_db.databases)

        # Monkey-patch bobo_application to use the new database
        Zope2.bobo_application._db = wrapper_db

        def cleanup():
            Zope2.bobo_application._db = base_db

        return cleanup, wrapper_db

    return orig_db, db_layer


class ZopeTestEnvironment:
    def __init__(self, orig_db, db_layer):
        self.orig_db = orig_db
        self.db_layer = db_layer

    wsgi_app = staticmethod(wsgi_publish)


def zope_test_environment(buildout_part_name):
    """Set up a Zope test environment for the given buildout part."""
    from os import path

    nodemo = False
    if '--nodemo' in sys.argv:
        nodemo = True
        sys.argv.remove('--nodemo')

    argv_orig = list(sys.argv)
    sys.argv[1:] = []

    buildout_root = path.dirname(path.dirname(sys.argv[0]))
    orig_conf_path = path.join(buildout_root, 'parts', buildout_part_name,
                               'etc', 'zope.conf')
    orig_db, db_layer = zope_startup(orig_conf_path, nodemo)

    sys.argv[:] = argv_orig

    return ZopeTestEnvironment(orig_db, db_layer)
