""" Installer
"""
from setuptools import setup, find_namespace_packages
from sys import version_info

requires = []
if version_info < (2, 5):
    requires.append('pysqlite')

setup(name='naaya.sql',
      version='2.0',
      description="",
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      )
