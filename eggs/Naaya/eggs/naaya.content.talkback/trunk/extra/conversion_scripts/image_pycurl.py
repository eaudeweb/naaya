import pycurl
import os, sys

def perform(curl):
    """ call curl.perform and check for errors """
    try:
        curl.perform()
    except:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

def upload_image(curl, url, filepath):
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.HTTPPOST, [('file', (curl.FORM_FILE, filepath))])
    #curl.setopt(curl.VERBOSE, 1)

    perform(curl)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "USAGE: python %s <foldername>" % sys.argv[0]
        sys.exit(255)

    if not os.path.exists(sys.argv[1]):
        print "Error: the file '%s' does not exist" % sys.argv[1]
        sys.exit(254)

    #NEADS A URL WITH HTML AUTHENTICATION AND USERNAME AND PASSWORD
    super_url = 'http://tbconsultation.edw.ro/site/demo/urban-environment/.images/manage_main'
    username = 'admin'
    password = 'admin'

    curl = pycurl.Curl()
    #curl.setopt(pycurl.PROXY, '127.0.0.1:8888')
    curl.setopt(pycurl.URL, super_url)
    curl.setopt(pycurl.USERPWD, username+':'+password)

    perform(curl)

    #NEEDS THE URL FOR THE FORM TO UPLOAD THE IMAGE
    url = 'http://tbconsultation.edw.ro/site/demo/urban-environment/.images/manage_addProduct/ExtFile/manage_addExtImage'
    for fname in os.listdir(sys.argv[1]):
        if fname.endswith('.html'):
            continue
        if fname.endswith('.pdf'):
            continue
        print 'Uploading ', fname
        upload_image(curl, url, sys.argv[1] + '\\' + fname)

    curl.close()


