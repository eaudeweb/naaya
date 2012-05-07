from path import path

instance_path = path(__file__).parent

secret_key_path = instance_path/'secret_key.txt'
if secret_key_path.isfile():
    SECRET_KEY = secret_key_path.text().strip()

DATABASE_URI = "postgresql://edw:edw@localhost/reportdb"
TESTING_DATABASE_URI = "postgresql://edw:edw@localhost/reportdb_test"
ZOPE_TEMPLATE_PATH = 'http://projects.eionet.europa.eu/seris-revision/report_templates/'
HTTP_PROXIED = True
ZOPE_TEMPLATE_CACHE = True
