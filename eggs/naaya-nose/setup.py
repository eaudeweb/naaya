from setuptools import setup, find_packages

setup(
    name='naaya-nose',
    version='0.4.6',
    author='Eau de Web',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['WebOb', 'zope.testrunner'],
    entry_points={'console_scripts': ['nytest = naaya_nose:main']},
)
