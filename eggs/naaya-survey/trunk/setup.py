from setuptools import setup, find_packages

setup(
    name='naaya-survey',
    version="1.2.53",
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro/',
    license='MPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Naaya',
                      'xlwt',
                      'pdfkit',
                      'naaya.i18n >= 1.1.8'],
)
