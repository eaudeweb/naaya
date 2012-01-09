from setuptools import setup, find_packages

setup(
    name='NaayaBundles-Groupware',
    description = "Server-specific bundles, Groupware at EEA",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.groupware'],
)
