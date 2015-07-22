from setuptools import setup, find_packages
import os
NAME = 'Products.CHMRegistrationDec2009'
version = open('version.txt', 'r').read().strip()

setup(name=NAME,
      version=version,
      description="CHMRegistrationDec2009",
      long_description=open("README.txt").read() + "\n",
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Eau De Web',
      author_email='office@eaudeweb.ro',
      url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/Naaya/Products.CHMRegistrationDec2009',
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
