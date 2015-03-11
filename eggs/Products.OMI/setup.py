from setuptools import setup, find_packages

setup(
    name='Products.OMI',
    version='1.2',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Naaya >= 3.4.15'],
)
