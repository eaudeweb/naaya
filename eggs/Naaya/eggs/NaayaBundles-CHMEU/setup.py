from setuptools import setup, find_packages

setup(
    name='NaayaBundles-CHMEU',
    description = "Server-specific bundles, CHM at EEA",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.chm'],
)
