from setuptools import setup, find_packages
import os
from getversion import get_version

version = get_version()

setup(name='naaya.groupware',
      version=version,
      description="Naaya Groupware",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='naaya groupware',
      author='David Batranu',
      author_email='david@eaudeweb.ro',
      url='',
      license='MPL',
      packages=['naaya', 'Products'],
      namespace_packages=['naaya', 'Products'],
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
