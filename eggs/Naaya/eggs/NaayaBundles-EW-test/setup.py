from setuptools import setup, find_packages

setup(
    name='NaayaBundles-EW-test',
    description = "Server-specific bundles, EW test sites",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.envirowindows'],
)

