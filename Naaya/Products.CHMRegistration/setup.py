from setuptools import setup, find_packages
import os
NAME = 'Products.CHMRegistration'
version = open('version.txt', 'r').read().strip()

setup(name=NAME,
      version=version,
      description="CHMRegistration",
      long_description=open("README.txt").read() + "\n",
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Eau De Web',
      author_email='office@eaudeweb.ro',
      url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/Naaya/Products.CHMRegistration',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )