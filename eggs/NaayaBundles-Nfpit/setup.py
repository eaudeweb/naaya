from setuptools import setup, find_packages

setup(
    name='NaayaBundles-Nfpit',
    description = "Server-specific bundles, NFP-IT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.groupware'],
)
