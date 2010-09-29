##############################################################################
#
# Copyright (c) 2000-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Shared LDAPUserFolder test configuration data

$Id: config.py 1695 2009-02-08 08:21:58Z jens $
"""

defaults = { 'title'  : 'LDAP User Folder'
           , 'server' : 'localhost:389'
           , 'login_attr' : 'cn'
           , 'uid_attr': 'cn'
           , 'users_base' : 'ou=people,dc=dataflake,dc=org'
           , 'users_scope' : 2
           , 'roles' : 'Anonymous'
           , 'groups_base' : 'ou=groups,dc=dataflake,dc=org'
           , 'groups_scope' : 2
           , 'binduid' : 'cn=Manager,dc=dataflake,dc=org'
           , 'bindpwd' : 'mypass'
           , 'binduid_usage' : 1
           , 'rdn_attr' : 'cn'
           , 'local_groups' : 0
           , 'implicit_mapping' : 0
           , 'use_ssl' : 0
           , 'encryption' : 'SHA'
           , 'read_only' : 0
           , 'extra_user_filter' : ''
           }

alternates = { 'title'  : 'LDAPUserFolder'
             , 'server' : 'localhost:1389'
             , 'login_attr' : 'uid'
             , 'uid_attr': 'uid'
             , 'users_base' : 'ou=people,dc=type4,dc=org'
             , 'users_scope' : 0
             , 'roles' : 'Anonymous, SpecialRole'
             , 'groups_base' : 'ou=groups,dc=type4,dc=org'
             , 'groups_scope' : 0
             , 'binduid' : 'cn=Manager,dc=type4,dc=org'
             , 'bindpwd' : 'testpass'
             , 'binduid_usage' : 2
             , 'rdn_attr' : 'uid'
             , 'local_groups' : 1
             , 'implicit_mapping' : 0
             , 'use_ssl' : 1
             , 'encryption' : 'SSHA'
             , 'read_only' : 1
             , 'obj_classes' : 'top, person, inetOrgPerson'
             , 'extra_user_filter' : '(special=true)'
             }

satellite_defaults= { 'title' : 'Satellite'
                    , 'luf' : '/luftest/acl_users'
                    , 'recurse' : 0
                    , 'groups_base' : 'ou=special,dc=dataflake,dc=org'
                    , 'groups_scope' : 2
                    }

user = { 'cn' : 'test'
       , 'sn' : 'User'
       , 'mail' : 'joe@blow.com'
       , 'givenName' : 'G\xc3\xbcnther'
       , 'objectClasses' : ['top', 'person']
       , 'user_pw' : 'mypass'
       , 'confirm_pw' : 'mypass'
       , 'user_roles' : ['Manager']
       , 'mapped_attrs' : {'objectClasses' : 'Objektklassen'}
       , 'multivalued_attrs' : ['objectClasses']
       , 'ldap_groups' : ['Group1', 'Group2']
       }

manager_user = { 'cn' : 'admin'
               , 'sn' : 'Manager'
               , 'givenName' : 'Test'
               , 'user_pw' : ''
               , 'confirm_pw' : ''
               , 'user_roles' : ['Manager', 'Administrator']
               , 'ldap_groups' : ['Group3', 'Group4']
               }

user2 = { 'cn' : 'test2'
        , 'sn' : 'User2'
        , 'mail' : 'joe2@blow.com'
        , 'givenName' : 'Test2'
        , 'objectClasses' : ['top', 'posixAccount']
        , 'user_pw' : 'mypass'
        , 'confirm_pw' : 'mypass'
        , 'user_roles' : ['Manager']
        , 'mapped_attrs' : {'objectClasses' : 'Objektklassen'}
        , 'multivalued_attrs' : ['objectClasses']
        , 'ldap_groups' : ['Group1', 'Group2']
        }


