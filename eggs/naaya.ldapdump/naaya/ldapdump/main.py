import os.path
import ldap
import ldapurl
import logging
import yaml
from datetime import datetime
import itertools
import operator
try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3


log = logging.getLogger('naaya.ldapdump')
log.setLevel(logging.DEBUG)

def get_config(config_path):
    try:
        file = open(config_path)
    except IOError, e:
        return {'_root_path': os.path.dirname(__file__),
                'sqlite': {'path': ''}}
    try:
        config = yaml.load(file)
        config['_root_path'] = os.path.abspath(os.path.dirname(config_path))
        return config
    finally:
        file.close()

def get_db_path(config):
    return os.path.join(config['_root_path'],
                        config['sqlite']['path'])


class LDAPConnection(object):
    def __init__(self, host, port, encoding, dn='', password=''):
        """
        Connects to a LDAP server
        can raise ldap.LDAPError
        """
        if not host.startswith('ldap://'):
            uri = 'ldap://' + host
        else:
            uri = host

        if port != 389:
            uri += ':' + str(port)

        log.debug('Connecting to %s', uri)

        ldap_conn = ldap.initialize(uri)
        ldap_conn.protocol_version = ldap.VERSION3

        if dn != '' and password != '':
            log.debug('Binding %s', dn)
            ldap_conn.simple_bind_s(dn, password)

        self._ldap_url = ldapurl.LDAPUrl(uri)
        self._connection = ldap_conn
        self._encoding = encoding

    def get_schema(self):
        subschemasubentry_dn = self._connection.search_subschemasubentry_s(
                self._ldap_url.dn)
        if subschemasubentry_dn is None:
            log.error("Couldn't find the schema subentry")
            return None

        if self._ldap_url.attrs is not None:
            schema_attrs = self._ldap_url.attrs
        else:
            schema_attrs = ldap.schema.subentry.SCHEMA_ATTRS

        subschemasubentry_entry = self._connection.read_subschemasubentry_s(
                                    subschemasubentry_dn, attrs=schema_attrs)

        return ldap.schema.SubSchema(subschemasubentry_entry)

    def get_values(self, baseDN):
        """
        Gets all the information from the baseDN (full subtree)
        can raise ldap.LDAPError
        """
        log.debug('Starting search %s', baseDN)

        schema = self.get_schema()
        returned = self._connection.search_s(baseDN, ldap.SCOPE_SUBTREE)

        # convert values to unicode
        ret = {}
        for dn, attr_dict in returned:
            ret[dn] = {}
            for attr, values in attr_dict.items():
                syntax = schema.get_syntax(attr)
                if syntax in ldap.schema.models.NOT_HUMAN_READABLE_LDAP_SYNTAXES:
                    ret[dn][attr] = {'type': 'binary', 'values': values}
                else:
                    try:
                        ret[dn][attr] = {
                                'type': 'text',
                                'values': [v.decode(self._encoding) for v in values],
                                }
                    except UnicodeDecodeError:
                        log.exception('dn:%s attr:%s', dn, attr)
        return ret

def get_ldap_connection(config):
    host = config['ldap']['host']
    port = config['ldap'].get('port', 389)
    encoding = config['ldap']['encoding']
    dn = config['ldap'].get('dn', '')
    password = config['ldap'].get('password', '')

    return LDAPConnection(host, port, encoding, dn, password)


def write_values(cursor, results_list):
    cursor.execute("DROP TABLE IF EXISTS LDAPMapping")
    cursor.execute(
        "CREATE TABLE LDAPMapping(id INTEGER PRIMARY KEY ASC, dn, attr, value)"
    )

    cursor.execute("DROP TABLE IF EXISTS LDAPMappingBlobs")
    cursor.execute(
        "CREATE TABLE LDAPMappingBlobs(id INTEGER PRIMARY KEY ASC, dn, attr, value BLOB)"
    )
    for result in results_list:
        for dn, attrs in result.items():
            for attr, wvalues in attrs.items():
                if wvalues['type'] == 'text':
                    for value in wvalues['values']:
                        try:
                            text = ('INSERT INTO LDAPMapping'
                                    '(dn, attr, value) '
                                    'VALUES (?, ?, ?)')
                            cursor.execute(text, (dn, attr, value))
                        except:
                            log.exception("Error inserting "
                                          "(dn=%s, attr=%s, value=%s)",
                                          dn, attr, value)
                            raise
                elif wvalues['type'] == 'binary':
                    for value in wvalues['values']:
                        try:
                            text = ('INSERT INTO LDAPMappingBlobs'
                                    '(dn, attr, value) '
                                    'VALUES (?, ?, ?)')
                            cursor.execute(text, (dn, attr, buffer(value)))
                        except:
                            log.exception("Error inserting "
                                          "(dn=%s, attr=%s, value=%s)",
                                          dn, attr, '<binary>')
                            raise

def reset_dump_timestamp(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS LDAPMetadata"
                   "(key PRIMARY KEY, value)")
    cursor.execute("INSERT OR REPLACE INTO LDAPMetadata(key, value) "
                   "VALUES ('date', ?)", (datetime.now().isoformat(),))

def save_results(config, results_list):
    db_path = get_db_path(config)

    db_conn = sqlite3.connect(db_path)
    cursor = db_conn.cursor()
    try:
        write_values(cursor, results_list)
        reset_dump_timestamp(cursor)
    except:
        log.exception("Error saving ldap results")
        raise
    else:
        db_conn.commit()
        log.info("Successfully dumped ldap data")
    cursor.close()

def setup_log_handler(config):
    logging_config = config.get('logging', {})
    if 'file' not in logging_config:
        return

    log_file_path = os.path.join(config['_root_path'], logging_config['file'])
    handler = logging.FileHandler(log_file_path)
    handler.setLevel(getattr(logging, logging_config.get('level', "INFO")))

    msg_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    handler.setFormatter(logging.Formatter(msg_format))

    log.addHandler(handler)

def dump_ldap(config_path):
    """ Perform a dump of an LDAP database according to the config file. """
    config = get_config(config_path)
    setup_log_handler(config)
    log.debug('Starting dump of LDAP data')
    dn_list = config['ldap']['root_DNs']

    try:
        ldap_conn = get_ldap_connection(config)
        results_list = []
        for dn in dn_list:
            values = ldap_conn.get_values(dn)
            results_list.append(values)
    except:
        log.exception("Error getting ldap values")
        raise
    else:
        save_results(config, results_list)


def get_db_meta(db_path, key):
    db_conn = sqlite3.connect(db_path)
    try:
        cursor = db_conn.cursor()
        try:
            text = "SELECT value FROM LDAPMetadata WHERE key=?"
            row = cursor.execute(text, (key,)).fetchone()
            return row[0]
        except sqlite3.OperationalError, e:
            log.exception("Error getting value for key %s", key)
            raise KeyError, key
    finally:
        db_conn.close()

class DumpReader(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def latest_timestamp(self):
        try:
            return get_db_meta(self.db_path, 'date')
        except KeyError:
            return None

    def _get_dump_items(self):
        db_conn = sqlite3.connect(self.db_path)
        cursor = db_conn.cursor()
        text = "SELECT dn, attr, value FROM LDAPMapping ORDER BY dn, attr"
        cursor.execute(text)

        blobcursor = db_conn.cursor()
        text = "SELECT dn, attr, value FROM LDAPMappingBlobs ORDER BY dn, attr"
        blobcursor.execute(text)

        # iterate both and match by dn
        attriter = itertools.groupby(cursor, operator.itemgetter(0))
        blobiter = itertools.groupby(blobcursor, operator.itemgetter(0))
        try:
            blob_dn, blob_iter = blobiter.next()
        except StopIteration:
            blob_dn = None

        for dn, iter in attriter:
            tuples = [(attr, value) for _dn, attr, value in iter]
            if blob_dn == dn: # match in iteration
                tuples.extend([(attr, str(value)) for _dn, attr, value in blob_iter])
                try:
                    blob_dn, blob_iter = blobiter.next()
                except StopIteration:
                    blob_dn = None
            yield dn, tuples

        db_conn.close()

    def get_dump(self):
        log.debug('Starting read of dump')
        for dn, tuples in self._get_dump_items():
            mapping = {}
            for attr, iter in itertools.groupby(tuples, operator.itemgetter(0)):
                values = [value for _attr, value in iter]
                if len(values) == 1:
                    mapping[attr] = values[0]
                elif len(values) > 1:
                    mapping[attr] = values
            mapping[u'dn'] = dn
            yield dn, mapping

def get_reader(config_path):
    config = get_config(config_path)
    db_path = get_db_path(config)

    return DumpReader(db_path)
