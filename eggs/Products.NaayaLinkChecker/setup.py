from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='Products.NaayaLinkChecker',
      version=version,
      description="Naaya LinkChecker",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='naaya link checker',
      author='Cornel Nitu',
      author_email='cornel@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      license='GPL',
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
