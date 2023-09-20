from setuptools import setup, find_packages

setup(name='edw.circaimport',
      version='1.3.15',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points={'console_scripts':
                    ['circaimport = edw.circaimport:demo',
                     'tsv2csv = edw.circaimport:tsv2csv',
                     'zip_export = edw.circaimport:do_export']},
      )
