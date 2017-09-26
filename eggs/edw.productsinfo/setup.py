from setuptools import setup, find_packages
import os

NAME = 'edw.productsinfo'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="Extract Zope Products info",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope products json',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['edw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'simplejson',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
