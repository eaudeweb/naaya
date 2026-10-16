from setuptools import setup, find_namespace_packages

setup(
    name='edw-cookiecrumbler',
    version='2.2.dev0',
    packages=find_namespace_packages(include=['Products.*']),
    install_requires=[
        'Zope',
    ],
)
