Installing Envirowindows
========================

Prerequisites
-------------
Before we can create a buildout to install the portals, there are a few
prerequisites to take care of. Please refer to `Installing Naaya
<http://naaya.eaudeweb.ro/docs/installation.html>`_, in order to install
Python, Zope server and Naaya, while using the configuration files
provided here:
 * buildout.cfg
 * ew.cfg
 * test.cfg
 * technologies.cfg
 * common.cfg
 * versions.cfg

The following commands should be run using the `zope` user.

Buildout
--------
You need to execute the following commands::

    $ python bootstrap.py
    $ bin/buildout


Configure the LDAP cache
------------------------
- add config file for ldapdump::

    $ vim var/ldapdump/config.yaml

::

    ldap:
        host: ldap.eionet.europa.eu
        encoding: utf-8
    root_DNs:
        - ou=Users,o=EIONET,l=Europe

    sqlite:
        path: ./ldap_eionet_europa_eu.db

    logging:
        file: ./log.txt


- add a cron job to update the ldapdump every day::

    $ crontab -e

::

 0 2 * * * cd /var/local/seionet/groupware/ && ./bin/dump_ldap

Start the Zope instances
------------------------
::

    $ bin/zeoserver-ew start
    $ bin/zope-instance-ew-0 start
    $ bin/zope-instance-ew-1 start
    $ bin/zope-instance-test start
    $ bin/zope-instance-technologies start
    $ bin/poundctl start

To test your installation access the URLs:
 * http://localhost:16082 - for envirowindows
 * http://localhost:16080 - for technologies
 * http://localhost:16083 - for test


- add a cron job to provide the server with heartbeat every 15 minutes::

    $ crontab -e

::

 */15 * * * * curl http://localhost:8080/cron_heartbeat >/dev/null 2>&1

