from setuptools import setup, find_packages

setup(name='Naaya',
      version='1.0dev',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'naaya.flowplayer',
          'contentratings',
          'Products.TextIndexNG3 >= 3.2.11',
          'itools == 0.20.6',
              # for Windows, download and install DLLs from
              # http://naaya.eaudeweb.ro/eggshop/glib-dlls.zip
          'feedparser >= 4.1',
          'BeautifulSoup >= 3.0.7a',
          'simplejson >= 2.0.9',
          'vobject >= 0.8.1c',
          'gdata >= 2.0.5',
          'mimeparse >= 0.1.2',

          # only used for testing:
          'twill >= 0.9',
          'webob',
      ]
)
