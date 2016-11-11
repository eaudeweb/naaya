from setuptools import setup, find_packages

setup(name='naaya.groupware',
      version='1.4.43',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 3.3.35',
          'naaya.content.bfile',
          'eea.usersdb >= 1.2.0',
          'collective.autopermission == 1.0b2',
      ]
      )
