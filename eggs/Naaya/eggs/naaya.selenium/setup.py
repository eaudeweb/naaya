from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='naaya.selenium',
      version=version,
      description="a Selenium functional test suite for Naaya",
      long_description=open("README.rst").read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Eaudeweb',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro/',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['naaya'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'selenium',
          'wsgiref',
          # -*- Extra requirements: -*-
      ],
      )
