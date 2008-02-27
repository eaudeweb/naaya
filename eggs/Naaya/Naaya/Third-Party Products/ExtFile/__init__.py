__doc__ = """ExtFile initialization module. """
__version__ = '1.5.6'

def initialize(context): 
    """Initialize the ExtFile product."""
    
    import ExtFile
    import ExtImage 

    try: 
        """Try to register the product."""
        
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
            
        # Mark as five:deprecatedManageAddDelete for Zope >= 2.9
        try:
            from Products.Five.eventconfigure import setDeprecatedManageAddDelete
        except ImportError:
            pass
        else:
            setDeprecatedManageAddDelete(ExtFile.ExtFile)
            setDeprecatedManageAddDelete(ExtImage.ExtImage)
    
    except:
        """If you can't register the product, tell someone."""
        
        import sys, traceback, string
        type, val, tb = sys.exc_info()
        sys.stderr.write(string.join(traceback.format_exception(type, val, tb), ''))
        del type, val, tb

# Import transaction module
try:
    import Zope2
except ImportError:
    # Zope <= 2.7
    import transaction_ as transaction
else:
    import transaction

