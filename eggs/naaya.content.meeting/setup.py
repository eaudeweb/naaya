from setuptools import setup, find_namespace_packages

setup(name='naaya.content.meeting',
      version='2.0.1.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_namespace_packages(include=['naaya.content.meeting*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 6.0.3',
          'naaya-survey >= 2.0.0',
          'html2text',
      ],
      )
