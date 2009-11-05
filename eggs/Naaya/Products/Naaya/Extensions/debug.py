def debug(self, REQUEST, RESPONSE):
    RESPONSE.setHeader('Content-Type', 'text/plain')
    RESPONSE.write('invoking pdb...\n')
    RESPONSE.flush()
    import pdb; pdb.set_trace()
    RESPONSE.write('done.\n')
