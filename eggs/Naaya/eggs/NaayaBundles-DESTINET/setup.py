from setuptools import setup, find_packages

setup(
        name='NaayaBundles-DESTINET',
        description='Server-specific bundles, Destinet',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=['naaya.envirowindows'],
)
