""" Talkback setup """
from setuptools import setup, find_namespace_packages

setup(name='naaya.content.talkback',
      version='2.0.3.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      # Not Products.NaayaContent itself: naaya.content-compat provides it with __file__
      packages=find_namespace_packages(
          include=['naaya.content.talkback*', 'Products.NaayaContent.*']),
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
