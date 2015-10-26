from setuptools import setup, find_packages

setup(name='naaya.chm',
      version='3.0.30',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 3.2.4',
          'naaya.photoarchive',
          'Products.NaayaLinkChecker',
          'Products.NaayaNetRepository',
          'Products.NaayaGlossary',
          'Products.NaayaCalendar',
          'Products.NaayaForum'
      ]
      )
