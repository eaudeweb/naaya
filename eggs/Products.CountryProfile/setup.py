from setuptools import setup, find_packages
import os

NAME = 'Products.CountryProfile'
VERSION = open(os.path.join(*NAME.split('.') + ['version.txt'])).read().strip()

setup(name=NAME,
      version=VERSION,
      description="",
      long_description=open("README.rst").read() + "\n",
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
      ],
      keywords='',
      author='EaudeWeb',
      author_email='office@eaudeweb.ro',
      url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/Products.CountryProfile/',
      license='MPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['MySQL-python', 'pygooglechart']
)
