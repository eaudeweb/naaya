""" Installer
"""
from setuptools import setup, find_namespace_packages

setup(name='Products.NaayaCalendar',
      version='2.0.2.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='MPL',
      packages=find_namespace_packages(include=['Products.*']),
      include_package_data=True,
      zip_safe=False,
      )
