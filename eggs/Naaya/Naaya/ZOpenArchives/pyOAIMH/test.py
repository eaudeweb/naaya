import httplib


site_host = 'hal.ccsd.cnrs.fr:80'
site_url = '/oai/oai.php?verb=Identify'

#site_host = '193.48.120.114:14080'
#site_url = '/cinematic/exist_oai?verb=Identify'

h = httplib.HTTPConnection(site_host)

h.request('GET', site_url)

r1 = h.getresponse()
print r1.status, r1.reason
print r1.read()

h.close()

pass


##h.connect()

    

##print "site_host ", site_host
##h.putrequest('GET', site_url)
##h.putheader('Host', site_host)
##h.putheader('User-agent', 'Wget/1.8.2')
##h.endheaders()
##response = h.getresponse()
##returncode = response.status
##returnmsg = response.reason
##headers = response.msg

##data = None
##if returncode == 200:  # OK
##    data = response.read()
##h.close()
##print ( returncode, returnmsg, headers, data )

