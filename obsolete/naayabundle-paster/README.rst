naayabundle-paste
===================

This is a paster template used to generate naaya bundles on the disk.

Example usage::

        from paste.script import command
        command.run([
            'create',
            '-tnaayabundle', #Naaya bundle paster template
            'nybundle-chm', #Package name
            'parent=CHM', #Parent bundle
            #Rest of the boilerplate
            'version=1.0',
            'description=Something',
            'long_description=Long description',
            'keywords=naaya bundles',
            'author=Eau de Web',
            'author_email=contact@eaudeweb.ro',
            'license_name=MPL',
            'url=http://www.eaudeweb.ro/',
            'zip_safe=False'
        ])

This will generate a nybundle-chm directory containing the necessary
entry_points that allows loading of bundles.
