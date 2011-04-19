Users and Roles
================

Three concepts govern the security mechanism in Zope and therefore in Naaya
portals:

* *Users* - similar to the ones in operating systems. The user accounts have a
  case sensitive username and password; in Naaya, additional information is also
  attached for easier tracking (names and email address).
* *Permissions* - define granular rights that users might or might nor have.
  Permissions are not granted directly to individual users, but to roles.
* *Roles* - groups of users that receive the same set of permissions; after
  a role is defined, users are *granted* those roles either on the entire
  portal or just locally, on one or more folders. For instance, all users
  having the role of *Contributor* on the entire portal can submit content
  to the portal.

The security model of a Naaya-based portal is based on the concept that
*what you see is what you can do*, meaning that whenever a user sees the
link to an operation, he/she has the necessary rights to execute that operation.
By default a set of roles are defined:

* *Administrators* - can execute all operations available on the portal pages
  and administrative area, but not enter the :term:`ZMI`
* content *Contributors* - only allowed to add content
* technical *Managers*, with full rights to execute any set of operations
* *Anonymous*, who can only access portal content
* *Authenticated*, who can access portal content, copy objects, submit
  comments

The list of roles can be tailored according with each specific portal needs,
taking into account the wideness, skills and availability of the community
that provides content and administrates the website.
Once users are defined in the system (have an account), they may be granted
with any subset of the above roles on the entire portal or just on the
locations (folders) they need to perform the operations that fall under their
areas of expertise.

*Users' management -> Local users -> Assign roles to users*

The *Assign roles to users*  page allows selecting one/several users and
assigning them a role be it on the whole portal, or at folder level.
When assigning the role(s) to a user, administrators can choose if they want
to notify  the user by email on the role assignment.

Naaya allows additional user repositories to be added if necessary.
For instance, if your organisation already has users in a LDAP directory or in
a database, such repository can be plugged in and used along with the local
user repository (*acl_users*) for eliminating account duplication.

*Users' management -> Roles*

The Administration area offers the *Roles* tab for the listing of the
roles defined in that portal, and for the addition of new roles in
the portal. Upon editing a role, administrators see the role's
permissions and they can check or uncheck some of the permissions
granted.
