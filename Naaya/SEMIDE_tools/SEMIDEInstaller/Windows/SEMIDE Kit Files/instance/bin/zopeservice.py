##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
A Zope Windows NT service frontend.

Usage:

  Installation

    The Zope service should be installed by the Zope Windows
    installer. You can manually install, uninstall the service from
    the commandline.

      ntservice.py [options] install|update|remove|start [...]
           |stop|restart [...]|debug [...]

    Options for 'install' and 'update' commands only:

     --username domain\username : The Username the service is to run
                                  under

     --password password : The password for the username

     --startup [manual|auto|disabled] : How the service starts,
                                        default = manual

    Commands

      install : Installs the service

      update : Updates the service.  Use this if you change any
               configuration settings and need the service to be
               re-registered.

      remove : Removes the service

      start : Starts the service, this can also be done from the
              services control panel

      stop : Stops the service, this can also be done from the
             services control panel

      restart : Restarts the service

      debug : Runs the service in debug mode

    You can view the usage options by running this module without any
    arguments.

  Starting Zope

    Start Zope by clicking the 'start' button in the services control
    panel. You can set Zope to automatically start at boot time by
    choosing 'Auto' startup by clicking the 'statup' button.

  Stopping Zope

    Stop Zope by clicking the 'stop' button in the services control
    panel. You can also stop Zope through the web by going to the
    Zope control panel and by clicking 'Shutdown'.

  Event logging

    Service related events (such as startup, shutdown, or errors executing
    the Zope process) are logged to the NT application event log. Use the
    event viewer to see these events.

    Zope Events are still written to the Zope event logs.

"""
import sys, os

# these are replacements from mkzopeinstance
PYTHON = r'@@ZOPE_PATH@@\zope\bin\python.exe'
SOFTWARE_HOME=r'@@ZOPE_PATH@@\zope\lib\python'
INSTANCE_HOME = r'@@ZOPE_PATH@@\instance'
ZOPE_HOME = r'@@ZOPE_PATH@@\zope'

ZOPE_RUN = r'%s\Zope\Startup\run.py' % SOFTWARE_HOME
CONFIG_FILE= os.path.join(INSTANCE_HOME, 'etc', 'zope.conf')
PYTHONSERVICE_EXE=r'%s\bin\PythonService.exe' % ZOPE_HOME

# Setup the environment, so sub-processes see these variables
parts = os.environ.get("PYTHONPATH", "").split(os.pathsep)
if SOFTWARE_HOME not in parts:
    parts = filter(None, [SOFTWARE_HOME] + parts)
    os.environ["PYTHONPATH"] = os.pathsep.join(parts)
os.environ["INSTANCE_HOME"] = INSTANCE_HOME

# Ensure SOFTWARE_HOME is on our current sys.path so we can import the
# nt_svcutils package.
if SOFTWARE_HOME not in sys.path:
    sys.path.insert(0, SOFTWARE_HOME)

from nt_svcutils.service import Service

servicename = 'EMWISZope'

class InstanceService(Service):
    _svc_name_ = servicename
    _svc_display_name_ = 'Zope (EMWISZope)'
    # _svc_description_ can also be set (but what to say isn't clear!)
    # If the exe we expect is not there, let the service framework search
    # for it.  This will be true for people running from source builds and
    # relying on pre-installed pythonservice.exe.
    # Note this is only used at install time, not runtime.
    if os.path.isfile(PYTHONSERVICE_EXE):
        _exe_name_ = PYTHONSERVICE_EXE

    process_runner = PYTHON
    process_args = '"%s" -C "%s"' % (ZOPE_RUN, CONFIG_FILE)

if __name__ == '__main__':
    import win32serviceutil
    win32serviceutil.HandleCommandLine(InstanceService)
