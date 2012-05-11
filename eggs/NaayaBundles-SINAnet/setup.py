from setuptools import setup, find_packages

setup(
    name='naayabundles_forum',
    description = "Server-specific bundles, SINAnet",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.groupware'],
)
