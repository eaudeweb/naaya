''' Naaya installer '''
from setuptools import setup, find_packages

setup(name='Naaya',
      version='6.0.0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      description="Naaya is a content management system based on Zope",
      keywords="cms zope",
      platforms=['OS Independent'],
      python_requires='>=3.10',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Zope',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries'
              ' :: Application Frameworks',
      ],

      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # Python 3rd party
          'beautifulsoup4',
          'feedparser >= 6.0',
          'lxml',
          'python-mimeparse',
          'Pillow',
          'dnspython',
          'pyquery',
          'requests',
          'bleach',
          'Unidecode',
          'vobject >= 0.9.6',
          'xlwt',
          'xlrd',

          # Zope
          'Zope >= 5.0',
          'zope.deprecation',
          'contentratings',

          # Customized 3rd party
          'edw-pycaptcha >= 0.3.1',

          # Naaya specific
          'naaya.content-compat',
          'naaya.flowplayer >= 1.1.7',
          'naaya.content.bfile >= 1.4.6',
          'naaya.i18n > 1.1.5',
          'naaya.cache >= 1.1',
      ],
      extras_require={
          'test': [
              'WebOb',
          ]
      },
      entry_points={'console_scripts': [
          'heartbeat = Products.Naaya.views:heartbeat',
      ]},
      )
