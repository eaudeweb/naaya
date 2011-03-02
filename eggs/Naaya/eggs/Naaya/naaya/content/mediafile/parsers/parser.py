""" Abstract parser module
"""
class Parser:
    """ Abstract parser class to subclass
    """
    def __init__(self, text=""):
        self.text = text
        
    def parse(self):
        """ Return unparsed text. Override this in your subclass in order to 
        parse text.
        """
        return self.text
