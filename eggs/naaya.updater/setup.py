from setuptools import setup, find_packages

setup(name='naaya.updater',
    version='1.2.12',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Naaya',
    ]
)
