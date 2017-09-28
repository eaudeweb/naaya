from zope.interface import Interface, Attribute


class IZipExportObject(Interface):
    """
    Export a given object as part of a Zip file. It's probably a good idea to
    subclass your adapter from
    `Products.NaayaCore.managers.zip_export_adapters.DefaultZipAdapter`
    which provides reasonable defaults for all the fields in this interface.
    """

    filename = Attribute("Name to use for exported file (of type `str`).")
    title = Attribute("Human-readable title. Will be written to `index.txt`.")
    meta_label = Attribute("`meta_label` or `meta_type`. Will be written to "
                           "`index.txt`.")
    timestamp = Attribute("Creation/modification date of the file.")
    export_as_folder = Attribute("Should this item be treated as a folder?")
    data = Attribute("Contents of the exported file (of type `str`).")
    skip = Attribute("Should we skip this object? If true, it will not be "
                     "included in the zip file.")
