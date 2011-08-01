from setuptools import setup, find_packages
import os

version = '1.20.1'

setup(name='edw-reportlab',
      version=version,
      description="Custom version with RTL text support of reportlab",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Python',
      author='EaudeWeb',
      author_email='office@eaudeweb.ro',
      url='http://svn.plone.org/svn/collective/',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
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
