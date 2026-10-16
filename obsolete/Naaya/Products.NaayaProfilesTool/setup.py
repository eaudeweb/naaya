from setuptools import setup, find_packages
import os

NAME = 'Products.NaayaProfilesTool'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(
    name=NAME,
    version=VERSION,
    description="User profiles for Naaya",
    long_description=open("README.rst").read() + "\n" +
                     open(os.path.join("docs", "HISTORY.rst")).read(),
    author='EaudeWeb',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro/',
    license='MPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Naaya'
    ]
)
