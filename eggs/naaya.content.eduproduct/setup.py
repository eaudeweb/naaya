from setuptools import setup, find_packages

setup(name='naaya.content.eduproduct',
      version='1.2.8',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 3.4.15',
      ],
      )
