def debug(self, REQUEST, RESPONSE):
    RESPONSE.setHeader('Content-Type', 'text/plain')
    RESPONSE.write('invoking pdb.set_trace() ...\n')
    RESPONSE.flush()
    import pdb; pdb.set_trace()
    RESPONSE.write('done.\n')

def interact(self, REQUEST, RESPONSE):
    RESPONSE.setHeader('Content-Type', 'text/plain')
    RESPONSE.write('invoking code.interact() ...\n')
    RESPONSE.flush()
    import code; code.interact(local={'self': self,
                                      'REQUEST': REQUEST,
                                      'RESPONSE': RESPONSE})
    print 'closed interactive session, finishing response'
    RESPONSE.write('done.\n')
