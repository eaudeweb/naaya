from setuptools import setup, find_namespace_packages

setup(name='edw.circaimport',
      version='2.0.2.dev0',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_namespace_packages(include=['edw.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya >= 6.0.1',
          'naaya.groupware >= 2.0.0',
      ],
      entry_points={'console_scripts':
                    ['circaimport = edw.circaimport:demo',
                     'tsv2csv = edw.circaimport:tsv2csv',
                     'zip_export = edw.circaimport:do_export']},
      )
