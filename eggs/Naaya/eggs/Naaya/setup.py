from setuptools import setup, find_packages
import os
import warnings

try:
    import pysvnaa
    pysvn_installed = True
except ImportError:
    warnings.warn('pysvn not installed')
    pysvn_installed = False

def get_svn_version():
    if not os.path.isdir('.svn'):
        return '1.0dev-r0'
    client = pysvn.Client()
    entry = client.info('.')
    revision = entry.revision.number
    return '1.0dev-r%s' % revision

def get_version():
    if pysvn_installed:
        return get_svn_version()
    return '1.0dev-r0'

version = get_version()

setup(name='Naaya',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=['Products', 'naaya'],
      namespace_packages=['Products', 'naaya'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
