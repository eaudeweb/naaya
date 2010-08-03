from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='zmibespin',
      version=version,
      description="Make every textarea in the Zope2 ZMI a bespin editor",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Python Javascript Bespin',
      author='Alexandru Plugaru',
      author_email='alexandru.plugaru@gmail.com',
      url='http://github.com/humanfromearth/zmibespin',
      license='MPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      )
