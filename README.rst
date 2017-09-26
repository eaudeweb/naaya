Naaya Groupware
===============

This package is a Naaya portal extension implementing Groupware
functionality for Eionet. It is intended to be installed in a Zope 2.10
instance. Please see `naaya/groupware/zope_customisation/README.rst`
which describes how to prepare a new Zope instance for use with
Naaya Groupware.

Other required actions
======================
Portal `nfp-eionet` displays a link in left menu to eionet
nfp-nrc editor. The address to this tool should be configured in buildout
in zope-instance section, like so:

environment-vars =
    EIONET_LDAP_EXPLORER http://www.eionet.europa.eu/eionet_ldap_explorer
