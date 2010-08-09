__doc__ = """ExtFile initialization module. """
__version__ = '2.0.2'

def initialize(context):
    """Initialize the ExtFile product."""

    import ExtFile
    import ExtImage

    context.registerClass(
        ExtFile.ExtFile,                        # Which is the addable bit?
        constructors = (                        # The first of these is called
            ExtFile.manage_addExtFileForm,      # when someone adds the product;
            ExtFile.manage_addExtFile),         # the second is named here so we
                                                # can give people permission to call it.
        icon = 'www/extFile.gif'                # This icon was provided by the
        )                                       # Zope 1 product-in-Python demo.

    context.registerClass(
        ExtImage.ExtImage,                      # Which is the addable bit?
        constructors = (                        # The first of these is called
            ExtImage.manage_addExtImageForm,    # when someone adds the product;
            ExtImage.manage_addExtImage),       # the second is named here so we
                                                # can give people permission to call it.
        icon = 'www/extImage.gif'               # This icon was provided by the
        )                                       # Zope 1 product-in-Python demo.

