# Python imports
from unittest import TestCase
import random
import os.path

# Zope imports
from OFS.Folder import Folder

# Naaya imports
from naaya.sql import new_db, NaayaSqlDb, DbMissing, naayasql

class NaayaSqlTestCase(TestCase):
    """
    TestCase for naaya.sql
    Recommendation: launch `watch -n 0.1 -p -d ls -l`
    in naaya.sql.DBS_FOLDER_PATH (default CLIENT_HOME - var/zope-instance)
    to observe dbfiles' changes

    """

    def setUp(self):
        if getattr(self, "generic_obj", None) is None:
            self.generic_obj = Folder()
        db = getattr(self.generic_obj, "db", None)
        if db is None:
            self.generic_obj.db = new_db()
        self.crs = self.generic_obj.db.cursor()

    def tearDown(self):
        dbfile = self.generic_obj.db._get_path()
        self.generic_obj.db.drop()
        self.assertFalse(os.path.exists(dbfile))
        self.crs.close()

    def test_queries(self):
        # autocommit by default: a new cursor (new connection) sees the data
        self.crs.execute("CREATE TABLE t(x integer primary key)")
        self.crs.execute("INSERT INTO t(x) values(?)", (13, ))
        crs = self.generic_obj.db.cursor()
        crs.execute("SELECT * from t")
        self.assertEqual(crs.fetchall(), [(13,)])
        crs.close()

    def test_db_file(self):
        db = self.generic_obj.db
        self.assertTrue(os.path.isfile(db._get_path()))
        self.assertEqual(os.path.dirname(db._get_path()),
                         naayasql.DBS_FOLDER_PATH)
        self.assertEqual(repr(db), '<NaayaSqlDb id: %s>' % db.db_id)
        other_db = new_db()
        self.assertNotEqual(other_db.db_id, db.db_id)
        other_db.drop()

    def test_transaction_isolation(self):
        crs = self.generic_obj.db.cursor(isolation_level='DEFERRED')
        crs.execute("CREATE TABLE t(x integer)")
        crs.connection.commit()
        crs.execute("INSERT INTO t(x) values(1)")
        other = self.generic_obj.db.cursor()
        other.execute("SELECT * from t")
        self.assertEqual(other.fetchall(), [])
        crs.connection.commit()
        other.execute("SELECT * from t")
        self.assertEqual(other.fetchall(), [(1,)])
        other.close()
        crs.close()

    def test_changedb(self):
        self.crs.close()
        self.generic_obj.db.drop()
        self.assertRaises(DbMissing, self.generic_obj.db.cursor)
        del self.generic_obj.db
        self.generic_obj.db = new_db()
        self.crs = self.generic_obj.db.cursor()

    def test_new_db_stress_test(self):
        """Create 100 dbs, each with 1 table with 1 record,
        then test them and drop them in reverse order

        """
        pool = []
        size = 50
        for i in range(size):
            pool.append(new_db())
        for i in range(size):
            crs = pool[i].cursor()
            crs.execute("CREATE TABLE t(x integer primary key)")
            crs.execute("INSERT INTO t(x) values(?)", (i, ))
            crs.close()
        for i in range(size):
            crs = pool[size-i-1].cursor()
            crs.execute("SELECT * from t")
            self.assertEqual(crs.fetchall(), [(size-i-1, )])
            crs.close()
            pool[size-i-1].drop()
