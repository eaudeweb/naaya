from setuptools import setup, find_packages

setup(name='naaya.monitor',
      version='1.3',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='https://github.com/eaudeweb/naaya/tree/master/eggs/naaya.monitor',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points={'console_scripts': [
          'add_monitor_stats = naaya.monitor.monitor:add_monitor_stats',
      ]},
      )
