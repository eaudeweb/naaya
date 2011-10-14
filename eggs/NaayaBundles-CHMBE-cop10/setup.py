from setuptools import setup, find_packages

setup(
    name='NaayaBundles-CHMBE-cop10',
    description = "Server-specific bundles, Belgian CHM cop10 sites",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['naaya.chm', 'Products.CHM2BE'],
)
