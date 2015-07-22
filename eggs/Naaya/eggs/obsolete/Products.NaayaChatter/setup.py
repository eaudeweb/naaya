from setuptools import setup, find_packages

setup(
    name='Products.NaayaChatter',
    version='1.3',
    author='EaudeWeb',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro/',
    license='MPL',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Naaya',
    ],
)
