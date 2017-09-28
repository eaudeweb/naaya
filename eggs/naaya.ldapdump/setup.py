from setuptools import setup, find_packages

import sys
extra_requires = []
if sys.version_info < (2, 5):
    extra_requires.append('pysqlite')

setup(name='naaya.ldapdump',
    version='1.0.3',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['python-ldap', 'PyYAML'] + extra_requires,
    entry_points={'console_scripts': [
        'dump_ldap = naaya.ldapdump.main:dump_ldap',
    ]},
)
