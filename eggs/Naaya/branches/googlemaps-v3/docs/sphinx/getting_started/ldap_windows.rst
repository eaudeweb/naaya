Installing LDAP User Folder
===========================

1. Install Python LDAP User Folder::

    easy_install Products.LDAPUserFolder

   This will install LDAP User Folder *and Python-ldap as a dependency*. The package
   Python-ldap 2.3.10 installed by easy_install is defective and it will fail to load.

2. Open ``Python\Lib\site-packages``, remove the folder
   ``python_ldap-2.3.10-py2.4-win32.egg`` and edit the file ``easy-install.pth``
   removing the line::

       ./python_ldap-2.3.10-py2.4-win32.egg

3. Download and install Python-ldap 2.3.10 (`python-ldap-2.3.10.win32-py2.4.exe
   <http://pypi.python.org/packages/2.4/p/python-ldap/python-ldap-2.3.11.win32-py2.4.exe>`_)
