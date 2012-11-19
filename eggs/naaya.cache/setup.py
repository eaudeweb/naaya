import sys
from setuptools import setup, find_packages


if sys.version_info >= (2, 6):
    install_requires = ['plone.memoize >= 1.1.1', ]
else:
    # actually Zope 2.10 branch
    install_requires = ['zope.component', 'zope.interface', 'zope.ramcache', ]


setup(name='naaya.cache',
      version='1.1',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      install_requires=install_requires,
      zip_safe=False)
