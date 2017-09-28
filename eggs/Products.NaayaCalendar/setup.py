""" Installer
"""
from setuptools import setup, find_packages

setup(name='Products.NaayaCalendar',
      version='1.3.11',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='MPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
  )
