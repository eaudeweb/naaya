from setuptools import setup, find_packages

setup(
    name='nystaging.forum',
    version='dev',
    author='Eau de Web',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'setuptools',
        'selenium',
        'wsgiref',
        'Naaya',
    ],
    zip_safe=False,
)
