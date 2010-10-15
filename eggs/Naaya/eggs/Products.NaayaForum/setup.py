from setuptools import setup, find_packages
import os

NAME = 'Products.NaayaForum'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(
    name=NAME,
    version=VERSION,
    description="Naaya Forum",
    long_description=open("README.rst").read() + "\n" +
                open(os.path.join("docs", "HISTORY.rst")).read(),
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    license='MPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[ 'setuptools',
        'Naaya',
        'naaya.sql'
    ],
)
