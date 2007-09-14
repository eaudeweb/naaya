# check for converter modules

import os, popen2

from zLOG import LOG, INFO, WARNING
from Products.TextIndexNG2.Registry import ConverterRegistry
from Products.TextIndexNG2 import fast_startup

if not fast_startup:

    converters = os.listdir(__path__[0])
    converters = [ c for c in converters if c.endswith('.py') and c != '__init__.py' ]

    for cv in converters:

        cv = cv[:-3]
        mod = __import__(cv, globals(), globals(), __path__)
        if not hasattr(mod,'Converter'): continue

        converter = mod.Converter()

        depends_on = getattr(converter, 'depends_on', None)
        if depends_on and os.name == 'posix':
            PO =  popen2.Popen3('which %s' % depends_on)
            out = PO.fromchild.read()
            PO.wait()
            del PO
            if out.find('no %s' % depends_on) > - 1 or out.lower().find('not found') > -1 or len(out.strip()) == 0:
                LOG('textindexng', WARNING, 'Converter "%s" not registered because executable "%s" could not be found' % (cv, depends_on))
                continue

        for t in converter.getType():
            ConverterRegistry.register(t, converter)
            LOG('textindexng', INFO, 'Converter "%s" for %s registered' % (cv, t))

    del converters
