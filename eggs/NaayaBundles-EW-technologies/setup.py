from setuptools import setup, find_packages

setup(
    name='NaayaBundles-EW-technologies',
    description = "Server-specific bundles, EW Technologies at EEA",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.envirowindows'],
)
