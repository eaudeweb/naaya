from setuptools import setup, find_packages

setup(name='Naaya',
      version='2.11.03', # March 2011
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      description = "Naaya is a content management system based on Zope2",
      keywords = "cms zope",
      platforms=['OS Independent'],
      classifiers = [
            'Development Status :: 5 - Production/Stable'
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
      ],

      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          #Python 3rd party
          'feedparser >= 4.1',
          'gdata >= 2.0.5',
          'itools',
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
          'zope.app.i18n',
          'zope.app.zapi',
          'zope.app.container',

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
