import sys
from setuptools import setup, find_packages


setup(name='naaya.cache',
      version='1.2',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'plone.memoize >= 1.1.1',
        # this should have been in setup.py of zope.ramcache 1.0
        'zope.location >= 3.5.4',
        ],
      zip_safe=False)
