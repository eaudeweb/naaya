#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='edw-ZOpenArchives',
    version='0.2',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    license='GPLv2',
    url='http://github.com/humanfromearth/edw-ZOpenArchives',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'pyoai >= 2.4.2',
        'pycountry',
        'sqlalchemy',
        'MySQL-python'
    ],
)
