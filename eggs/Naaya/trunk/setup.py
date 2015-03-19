from setuptools import setup, find_packages

setup(name='Naaya',
      version='3.4.17',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      description="Naaya is a content management system based on Zope2",
      keywords="cms zope",
      platforms=['OS Independent'],
      classifiers=[
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
          # Python 3rd party
          'BeautifulSoup',
          'feedparser >= 4.1',
          'gdata',
          'lxml',
          'mimeparse >= 0.1.2',
          'Pillow',
          'pydns',
          'pyquery',
          'requests',
          'scrubber',
          'simplejson >= 2.0.9',
          'Unidecode',
          'validate_email',
          'vobject >= 0.8.1c',
          'xlwt',
          'xlrd',

          # Zope
          'contentratings',
          'Products.TextIndexNG3 >= 3.2.11',

          # Customized 3rd party
          'edw-pycaptcha >= 0.3.1',
          'edw-extfile >= 2.0.2-edw1',

          # Naaya specific
          'naaya.content-compat',
          'naaya.flowplayer',
          'naaya.content.bfile >= 1.4.6',
          'naaya.i18n > 1.1.5',
          'naaya.cache >= 1.1',

          # Testing
          # 'twill',
          # 'WebOb',
      ],
      extras_require={
          'test': [
              'twill',
              'WebOb',
          ]
      }
      )
