"""Boot Zope for the tests from an instance zope.conf, without HTTP servers."""
import os
import re
from tempfile import mkdtemp, mkstemp

import ZODB.DB
from ZODB.DemoStorage import DemoStorage


def wsgi_publish(environ, start_response):
    """WSGI app that delegates to Zope's publish_module."""
    from ZPublisher.WSGIPublisher import publish_module
    return publish_module(environ, start_response)


def conf_for_test(zope_conf_path):
    """Temporary copy of zope.conf with a MappingStorage main database."""
    with open(zope_conf_path, encoding='utf-8') as f:
        conf = f.read()
    start = conf.index('<zodb_db main>\n') + len('<zodb_db main>\n')
    end = conf.index('</zodb_db>\n', start)
    conf = (conf[:start] + '    <mappingstorage>\n    </mappingstorage>\n'
            '    mount-point /\n' + conf[end:])
    # An empty instance home, so an emergency user in its access file stays out of the tests
    home = re.search(r'^%define INSTANCEHOME (.+)$', conf, re.M)
    if home:
        test_home = mkdtemp()
        # site.zcml and package-includes are read from INSTANCEHOME/etc
        os.symlink(os.path.join(home.group(1).strip(), 'etc'), os.path.join(test_home, 'etc'))
        conf = conf.replace(home.group(0), '%define INSTANCEHOME ' + test_home, 1)
    fd, path = mkstemp(suffix='.conf')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(conf)
    return path


class ZopeTestEnvironment:
    """The booted Zope: db_layer() stacks a DemoStorage on the current database."""

    wsgi_app = staticmethod(wsgi_publish)

    def db_layer(self):
        import Zope2
        base_db = Zope2.bobo_application._db
        # Remove from the databases dict to avoid a duplicate name error
        base_db.databases.pop(base_db.database_name, None)
        wrapper_db = ZODB.DB(storage=DemoStorage(base=base_db.storage),
                             database_name=base_db.database_name,
                             databases=base_db.databases)
        Zope2.bobo_application._db = wrapper_db

        def cleanup():
            Zope2.bobo_application._db = base_db

        return cleanup, wrapper_db


def zope_test_environment(zope_conf_path):
    """Configure and start Zope from zope_conf_path, on an empty database."""
    import Zope2
    from Zope2.Startup.run import configure_wsgi
    conf_path = conf_for_test(zope_conf_path)
    try:
        configure_wsgi(conf_path)
        app = Zope2.app()
        app._p_jar.close()
    finally:
        os.unlink(conf_path)
    return ZopeTestEnvironment()
