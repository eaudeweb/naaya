from setuptools import setup, find_namespace_packages

setup(name='naaya.sentry',
      version='1.0.0.dev0',
      description='Sentry integration for Naaya/Zope',
      long_description=(open('README.rst').read() + '\n' +
                        open('CHANGELOG.rst').read()),
      long_description_content_type='text/x-rst',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='https://github.com/eaudeweb/naaya/tree/master/eggs/naaya.sentry',
      packages=find_namespace_packages(include=['naaya.*']),
      include_package_data=True,
      zip_safe=False,
      python_requires='>=3.12',
      install_requires=[
          'sentry-sdk >= 2.0',
          'zope.globalrequest',
      ],
      )
