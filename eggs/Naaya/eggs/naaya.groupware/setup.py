from setuptools import setup, find_packages

setup(name='naaya.groupware',
      version='1.1.5',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya',
          'naaya.content.bfile',
          'eea.usersdb'
      ]
)
