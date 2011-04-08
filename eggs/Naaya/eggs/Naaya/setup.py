import os
from setuptools import setup, find_packages

setup(name='Naaya',
      version='2.11.03', # March 2011
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          #Python 3rd party
          'feedparser >= 4.1',
          'gdata >= 2.0.5',
          'itools == 0.20.6',
              # for Windows, download and install DLLs from
              # http://naaya.eaudeweb.ro/eggshop/glib-dlls.zip
          'lxml',
          'BeautifulSoup',
          'mimeparse >= 0.1.2',
          'simplejson >= 2.0.9',
          'vobject >= 0.8.1c',
          'Unidecode',

          #Zope
          'contentratings',
          'Products.TextIndexNG3 >= 3.2.11',

          #Customized 3rd party
          'edw-pycaptcha >= 0.3.1',
          'edw-localizer >= 1.2.3.3',
          'edw-extfile >= 2.0.2-edw1',

          #Naaya specific
          'naaya.content-compat',
          'naaya.flowplayer',

          #Testing
          
          # 'twill',
          # 'WebOb',
      ]
)
