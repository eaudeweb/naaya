# Copyright (c) 2003 Luke Francl
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# Using pre gets around recursion limit problems, but doesn't work with Ynicode
import pre as re 
import sys
import getopt
import os

class SearchAndReplace:
    """SearchAndReplace holds a compiled regular expression to be used for
searching and a replacement to be used to replace the regular expression's
match. Replacement defaults to the empty string."""
    def __init__(self, regex, replacement = ""):
        self.regex = regex
        self.replacement = replacement

    def __repr__( self ):
        return "Replace " + repr( self.regex.pattern ) + "with '" + self.replacement + "'"
    
# Some people, when confronted with a problem, think ``I know, I'll use
# regular expressions.'' Now they have two problems.
#                                                   -- jwz

searchAndReplacements = []

xmlns = re.compile( r"<html\s*?xmlns.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( xmlns , "<html>" ) )

meta_http = re.compile( r"<meta.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( meta_http ) )

# can break the recursion limit when using sre (the default implementation)
comment = re.compile( r"<!--.*?-->", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( comment ) )

body = re.compile( r"<body.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( body, "<body>") )

file_list = re.compile( r"<link rel=File-List.*?>", re.DOTALL)
searchAndReplacements.append( SearchAndReplace( file_list ) )

#div = re.compile( r"<div.*?>", re.DOTALL )
#searchAndReplacements.append( SearchAndReplace( div ) )

#end_div = re.compile( r"</div>" )
#searchAndReplacements.append( SearchAndReplace( end_div ) )

style_tag = re.compile( r"<style>" )
searchAndReplacements.append( SearchAndReplace( style_tag ) )

end_style_tag = re.compile( r"</style>" )
searchAndReplacements.append( SearchAndReplace( end_style_tag ) )

# can break the recursion limit when using sre (the default implementation)
if_statement = re.compile( r"<!\[.*?\]>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( if_statement ) )

#span = re.compile( r"<span.*?>", re.DOTALL )
#searchAndReplacements.append( SearchAndReplace( span ) )

#end_span = re.compile( r"</span>" )
#searchAndReplacements.append( SearchAndReplace( end_span ) )

#style = re.compile( r"\s*?style='.*?'", re.DOTALL )
#searchAndReplacements.append( SearchAndReplace( style ) )

#css_class = re.compile( r"\s*?class=[A-Za-z0-9]*", re.DOTALL )
#searchAndReplacements.append( SearchAndReplace( css_class ) )

# need regexps for o:, w:, and st1: and ends
office_namespace = re.compile( r"<o:.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( office_namespace ) )

end_office_namespace = re.compile( r"</o:.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( end_office_namespace ) )

word_namespace = re.compile( r"<w:.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( word_namespace ) )

end_word_namespace = re.compile( r"</w:.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( end_word_namespace ) )

smart_tags_namespace = re.compile( r"<st1:.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( smart_tags_namespace ) )

end_smart_tags_namespace = re.compile( r"</st1:.*?>", re.DOTALL )
searchAndReplacements.append( SearchAndReplace( end_smart_tags_namespace ) )

# didn't your mom tell you to clean up after yourself?
#kill_blank_lines = re.compile( r"^[\s].*$" )
#searchAndReplacements.append( SearchAndReplace( kill_blank_lines ) )

def remove_empty_lines( multiline_string ):
    lines = multiline_string.splitlines()

    while '' in lines:
        lines.remove('')

    no_empty_lines = "\n".join( lines )

    return no_empty_lines

def replace( searchReplace ):
    """Given a SearchAndReplace object, this function uses the
SearchAndReplace's regular expression to substitute the SearchAndReplace's
replacement in the global string word_html"""
    global word_html
    global debug
    if debug:
        print repr( searchReplace )
    word_html = searchReplace.regex.sub( searchReplace.replacement, word_html )

def unmungeFile( filename, output ):
    """Does most of the work. Given a filename for input and output (which
is either sys.stdout or a filename), this function reads filename for input
and stores it in the global word_html string, then calls map to execute
replace() on every SearchAndReplace in the searchAndReplacements list. Then
it writes the resulting HTML to output."""
    global word_html
    # read in file in string
    word_file = file(filename, "r")
    word_html = word_file.read()
    word_file.close()

    # do substitutions
    map( replace, searchAndReplacements )

    word_html = remove_empty_lines( word_html )

    # write it out
    if output == sys.stdout:
        word_file = sys.stdout
    else:
        word_file = file( output, "w" )
    
    word_file.write( word_html )
    word_file.close()

def unmungeString(p_string):
    """ The same as unmungeFile but it handles strings. """
    word_html = p_string

    # do substitutions
    for searchReplace in searchAndReplacements:
        word_html = searchReplace.regex.sub( searchReplace.replacement, word_html )
    word_html = remove_empty_lines( word_html )

    #return the result
    return word_html


def usage():
    """Prints usage information."""
    usage_string = """Usage:

word-unmunger filename.html [output.html]

  If a second filename is provided, the word-unmunger will write the output
  to that file. By default, it prints the output on the console.

word-unmunger --output-dir=<directory> file [file2 [file3 [...] ] ]

  Runs the Word Unmunger in batch mode. <directory> will be created if
  it does not exist and the output files will be written to that directory
  with the same name as they have now. No checking is done for files which
  have the same filename. If file is given as an absolute path, only the name
  (the last part of the path) will be used.

If --debug is used, the program will print out the regular expressions and
their replacement text as it runs them."""

    print usage_string
    sys.exit()
    
if __name__ == "__main__":
    global debug
    debug = 0
    
    longoptions = ["output-dir=", "help", "debug"]
    optlist = []
    files = []
    try:
      optlist, files = getopt.getopt( sys.argv[1:], '',  longoptions )
      if len(files) < 1:
            raise Exception
    except:
        usage()

    for option, arg in optlist:

        if option == "--debug":
            debug = 1
        
        if option == "--help":
            usage()

        if option == "--output-dir":
            if (not os.path.isdir( arg ) ):
                os.makedirs( arg )
                
            for f in files[:]:
                directory, fname = os.path.split( f )
                destination = os.path.join( arg, fname )
                unmungeFile( f, destination )
            sys.exit()

    if len(files) == 2:
        unmungeFile( files[0], files[1] )
    else:
        unmungeFile( files[0], sys.stdout )