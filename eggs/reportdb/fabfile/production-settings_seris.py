from path import path

instance_path = path(__file__).parent

secret_key_path = instance_path/'secret_key.txt'
if secret_key_path.isfile():
    SECRET_KEY = secret_key_path.text().strip()

DATABASE_URI = "postgresql://edw:edw@localhost/seris"
TESTING_DATABASE_URI = "postgresql://edw:edw@localhost/seris_test"
FRAME_URL = 'http://projects.eionet.europa.eu/seris-revision/report_templates/frame'
HTTP_PROXIED = True
ZOPE_TEMPLATE_CACHE = True
FRAME_COOKIES = ['__ac', '_ZopeId']
HTTP_PROXIED = True
