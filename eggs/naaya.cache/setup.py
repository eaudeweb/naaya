from setuptools import setup, find_packages

setup(name='naaya.cache',
      version='1.0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'plone.memoize >= 1.1.1',
          ],
      zip_safe=False)

