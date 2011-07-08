import sys
from App.config import getConfiguration

AOA_MODULE_RELOAD = getConfiguration().environment.get('AOA_MODULE_RELOAD', '')
def aoa_devel_hook(name):
    """ dynamically reload modules to speed up development """
    if AOA_MODULE_RELOAD:
        reload(sys.modules[name])
