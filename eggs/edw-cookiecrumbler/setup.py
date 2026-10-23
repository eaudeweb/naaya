from setuptools import setup, find_namespace_packages

setup(
    name='edw-cookiecrumbler',
    version='2.6.dev0',
    packages=find_namespace_packages(include=['Products.*']),
    include_package_data=True,
    install_requires=[
        'Zope',
    ],
)
