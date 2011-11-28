from setuptools import setup, find_packages

setup(
    name='NaayaBundles-EW',
    description = "Server-specific bundles, EW at EEA",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.envirowindows'],
)
