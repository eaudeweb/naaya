naayabundle-paste
===================

This is a paster template used to generate naaya bundles on the disk.

Usage::

        from paste.script import command
        command.run(['create', '-tnaayabundle', 'nybundle-chm'])

This will generate a nybundle-chm directory containing the necessary
entry_points that allows loading of bundles.
