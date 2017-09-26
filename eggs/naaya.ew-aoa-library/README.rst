EW Assessment of Assessments library viewer
===========================================

The "Assessment of Assessments" EnviroWindows portal contains a library
of environmental assessments, which is implemented as a Naaya Survey.
This viewer product creates a single Zope object that provides a useful
view into the library of assessments.

Installation
------------
Add ``naaya.ew-aoa-library`` to the Zope instance's eggs, add
``naaya.ew_aoa_library`` to the list of ZCMLs to be loaded, start up
Zope, and create a `Naaya EnviroWindows AoA Library Viewer` object.
`Survey path` is a path (relative to the site's root) to the
`Naaya Survey` that contains assessment data.

You also need to create a Python script in ZODB in the ``portal_map``
object, named ``custom_filter``, that receives two arguments (``filters``
and ``kwargs``), with the following content::
    for filter in filters:
        filter['meta_type'].append('Naaya EW_AOA Shadow Object')
    return filters


How it works
------------
The Viewer object browses the survey answers and creates shadow objects
on demand. A shadow object contains all relevant information from a
single survey answer, it's accessible via URL as a child of the Viewer
object, it's automatically indexed in the portal's catalog and shown on
the map, but never stored in the database. Whenever such an object is
accessed, it's generated from the original answer (and then cached in
memory).

Customizing a survey
--------------------
The `extra` folder contains a custom template and a custom validation
script, to be uploaded in a `NaayaSurvey` via ZMI.
