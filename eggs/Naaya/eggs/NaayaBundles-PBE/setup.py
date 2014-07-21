from setuptools import setup, find_packages

setup(
    name='NaayaBundles-PBE',
    description = "Server-specific bundles, PBE at EEA",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.groupware'],
)
