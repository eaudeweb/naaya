""" Installer
"""
from setuptools import setup, find_packages
from sys import version_info

requires = []
if version_info < (2, 5):
    requires.append('pysqlite')

setup(name='naaya.sql',
      version='1.2',
      description="",
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      )
