naaya.content.localizedbfile
=============================

This is a Blob file based content type for Naaya. It is similar to 
`naaya.content.bfile`_. The difference is that this content type has localized
blob files. It means that for each language in the portal this content type can 
have a different file.

For example:

        A portal has 2 languages: en, fr. We create a localized bfile with one
        english_version.zip which will be upload to the english part and a 
        french_version.zip to the french version.

This is useful when there are documents (pdfs, docs, excels) translated to 
different languages which can be uploaded to their correct language.

Installation
-----------------

Assuming that the installation environment is using `zc.buildout`_ and the 
zope-instance part is [zope-instance]::

        [zope-instance]
        recipe = plone.recipe.zope2instance
        eggs =
                Naaya
                naaya.content.bfile
                naaya.content.localizedbfile
        zcml =
                naaya.content.bfile
                naaya.content.localizedbfile

See install instructions of naaya.content.bfile. They apply to localized bfile
as well.

Testing
-----------
::

        nynose --with-naaya-portal naaya.content.localizedbfile

About
---------

This project was created by Emilia Ciobanu as part of her internship 
at Eau de Web (Bucharest)
