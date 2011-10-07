from setuptools import setup, find_packages
import os

NAME = 'Products.NaayaContent.NySimpleConsultation'
PATH = NAME.split('.') + ['version.txt']

setup(name=NAME,
      version='1.1.2',
      description="",
      long_description=open("README.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
      ],
      keywords='',
      author='EaudeWeb',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro/',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya',
      ],
)
