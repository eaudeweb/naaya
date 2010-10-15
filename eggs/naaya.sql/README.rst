naaya.sql - simple database connection interface for Naaya
==================================================================
This product provides the ability to ask and retrieve a connection
to an sqlite database.

Usage
=====

Creating a database::

 db = naaya.sql.new_db()
 your_object.my_db = db

`db` or `my_db` property of `your_object` is a naaya.sql.NaayaSqlDb 
persistent object. You can later on retrieve a cursor for the same database.

Retrieving a cursor for a database, executing queries::

 cursor = your_object.my_db.cursor()
 cursor.execute("CREATE TABLE t(x INTEGER PRIMARY KEY ASC, y, z)")
 # or simply:
 your_object.my_db.cursor().execute("DROP TABLE t")

`naaya.sql.NaayaSqlDb.cursor()` raises `naaya.sql.DbMissing` exception if db 
is missing (e.g. if the file was removed from the disk).

Deleting a database::

 your_object.my_db.drop()
 del your_object.my_db
