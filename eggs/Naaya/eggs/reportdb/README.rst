Quick installation
------------------

1. Check out the repository::

    svn co https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/reportdb
    cd reportdb

2. Create & activate a virtual environment::

    virtualenv sandbox --no-site-packages
    echo '*' > sandbox/.gitignore
    . sandbox/bin/activate

3. Install dependencies. Make sure to use `pip` from the virtual
   environment::

    pip install -r requirements-dev.txt

4. Create a configuration file::

    mkdir -p instance
    echo 'DEBUG = True' >> instance/settings.py
    echo 'SECRET_KEY = "something random"' >> instance/settings.py

5. Set up the PostgreSQL database::

    createdb reportdb
    psql reportdb -c 'create extension hstore'
    ./manage.py syncdb

6. Create a testing database and run the unit tests::

    createdb reportdb_test
    psql reportdb_test -c 'create extension hstore'
    nosetests

7. Run a test server::

    ./manage.py runserver

8. Deploy (after customizing `local_fabfile.py`)::

    fab deploy


Debian deployment
-----------------

To set up the PostgreSQL database in Debian, you need to install the
packages `postgresql-9.1`, `postgresql-contrib-9.1` and
`postgresql-server-dev-9.1`. Then create a database, enable the `hstore`
extension, and grant access to a user::

    root # su - postgres
    postgres $ psql template1
    psql (9.1.2)
    Type "help" for help.

    template1=# CREATE USER edw WITH PASSWORD 'edw';
    CREATE ROLE
    template1=# CREATE DATABASE reportdb;
    CREATE DATABASE
    template1=# GRANT ALL PRIVILEGES ON DATABASE reportdb TO edw;
    GRANT
    template1=# \q
    postgres $ psql reportdb
    reportdb=# create extension hstore;

Update the local settings::

    echo 'DATABASE_URI = "postgresql://edw:edw@localhost/reportdb"' >> instance/settings.py
    echo 'TESTING_DATABASE_URI = "postgresql://edw:edw@localhost/reportdb_test"' >> instance/settings.py


Development
-----------

ReportDB is developed using Flask_, with Jinja_ templates, and schema
defined with Flatland_. Data is stored in PostgreSQL using the special
hstore_ column type, so there's no need for schema migration scripts on
every change in the models.

.. _Flask: http://flask.pocoo.org/
.. _Jinja: http://jinja.pocoo.org/
.. _Flatland: http://dag-flatland.readthedocs.org/
.. _hstore: http://www.postgresql.org/docs/current/static/hstore.html
