""" Talkback setup """
from setuptools import setup, find_packages

setup(name='naaya.content.talkback',
      version='2.0.0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 6.0.1',
          'beautifulsoup4',
          'bleach[css]',
          'openpyxl',
          'xlrd',
          'xlsxwriter',
      ],
      )
