naaya.ldapdump - saving and querying a dump of ldap data
==========================================================================
 * connects to a ldap server and gets full subtree for a given dn list of
   root_DNs (all returned values are unicode)
 * saves the values gathered in a sqlite table with columns
   (dn, attr, value)
 * a reader can connect to the database and get the last timestamp
   (last update time) and a dictionary of all the data in the database
   {dn: {attr: [value]}}

A configuration file is needed. The file configures ldap server and
database path. An example configuration file is provided for the tests and
can be used as an example.

It's Naaya independent, but can be used with Naaya with some buildout
configuration.


Using nayaa.ldapdump with Naaya
================================
This assumes a buildout configuration for Naaya.

First you need to add the configuration file in::
 /var/local/buildout/var/ldapdump
replace with path to buildout:directory

You need to have the folowing lines to buildout.cfg::
 parts =
   ldapdump

 [ldapdump]
 recipe = zc.recipe.egg
 eggs = naaya.ldapdump
 arguments = "var/ldapdump/config.yaml"

Also in buildout.cfg in the zope instance recipe you need to have::
 zcml =
   naaya.ldapdump-meta
 zcml-additional =
   <configure xmlns:ld="http://ns.eaudeweb.ro/naaya.ldapdump">
     <ld:reader path="${buildout:directory}/var/ldapdump/config.yaml" />
   </configure>

Next you have to run buildout which will generate the dump_ldap script.

If you want you can add the script as a cron job::
 0 2 * * * /var/local/buildout/dump_ldap

