# Python imports
from unittest import TestCase
import random
import os.path

# Zope imports
from OFS.Folder import Folder

# Naaya imports
from naaya.sql import new_db, NaayaSqlDb, DbMissing

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
        self.crs.execute("CREATE TABLE t(x integer primary key)")
        self.crs.execute("INSERT INTO t(x) values(?)", (13, ))
        self.crs.execute("SELECT * from t")
        self.assertEqual(self.crs.fetchall(), [(13,)])

    def test_changedb(self):
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
            pool[i].cursor().execute("CREATE TABLE t(x integer primary key)")
            pool[i].cursor().execute("INSERT INTO t(x) values(?)", (i, ))
        for i in range(size):
            crs = pool[size-i-1].cursor()
            crs.execute("SELECT * from t")
            self.assertEqual(crs.fetchall(), [(size-i-1, )])
            crs.close()
            pool[size-i-1].drop()
