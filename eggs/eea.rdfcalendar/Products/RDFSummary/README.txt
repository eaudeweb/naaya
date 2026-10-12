README for RDFSummary

   RDFSummary is a product to display content from other web sites
   provided they make it available in RSS 0.90, Netscape RSS 0.91, Userland RSS 
   0.91, RSS 0.92, RSS 0.93, RSS 0.94, RSS 1.0, RSS 2.0, Atom, and CDF feeds.

   The benefit of doing it this way is that the data you get is not
   encumbered with HTML, giving you more flexibility when applying your
   own look and feel.

How to install
   First you need to install the feedparser Python module. You can download it
   from the project's Google code page (http://code.google.com/p/feedparser/).
   Unzip it, and then run: python setup.py install

   Some platforms, such as Mac OS X 10.2 and some versions of FreeBSD, do not
   include an XML parser in their Python distributions. In this case you must install
   PyXML (an advanced set of XML libraries that provide more functionality than the
   built-in XML libraries). Go to project's SourceForge page (http://pyxml.sourceforge.net/)
   download and install the latest version for your operating system. 

   After that, install RDFSummary in the Products folder and restart
   Zope. You will now be able to create objects of the type "RDF  Summary". 

How to use it

   When you add a new object of the type "RDF Summary" the form will ask you
   four questions: the id, title, URL of the RSS File and an optional proxy.
   You enter the URL that will return a correct format. If your RDF file is
   password protected you can specify authentication parameters like this:
   http://user:password@host.domain.com/file.rdf

   If nothing comes to mind, you can always try
   http://www.slashdot.org/slashdot.rdf. Last time I checked it was
   version 0.9. Otherwise, I have created some test files on Zope.org.

   Prefix all names with http://www.zope.org/Members/EIONET/RDFSummary/

   rdfexample1.rdf -- The first example from section 7 of the RSS 1.0 core
   specification
   
   rdfexample2.rdf -- The second example from section 7. Since this example
   uses an unsupported module RDFSummary will not be able to import it.

   When you have created the object, you must update or synchronize the
   object with the content on the remote webserver. Click Update to
   perform it. Most common mistake is bad encoding of the file in which
   case you get a syntax error or you have HTML tags somewhere in the
   title or description and these are not supported.

   There is also an optional property for a proxy-server. You enter the
   URL of the proxy as in http://proxy.mycompany.com:8080. Authenticated
   proxies are supported if you are using Python 2.1. To use an authenticated
   proxy, you enter the URL as in http://user:password@proxy.mycompany.com:8080.

   Let's say you have created a channel called slashdot. Then insert this
   in your dtml-document:
<pre>
&lt;dtml-with slashdot&gt;
  &lt;h1&gt;&lt;dtml-var "channel['title']"&gt;&lt;/h1&gt;
  &lt;dtml-var picture&gt;
  &lt;dtml-in items mapping&gt;
    &lt;p&gt;
    &lt;a href="&lt;dtml-var link&gt;"&gt;&lt;dtml-var title&gt;&lt;/a&gt;&lt;br&gt;
    &lt;dtml-if "_.has_key(&#39;description&#39;)"&gt;
      &lt;dtml-var description&gt;
    &lt;/dtml-if&gt;
    &lt;/p&gt;
  &lt;/dtml-in&gt;
&lt;/dtml-with&gt;
</pre>
   If you want your RDFSummary to import data on a regular basis, you
   can write a program which updates the channel by doing a GET on the update
   method as in lynx -source http://www.mysite.com/slashdot/update &gt;/dev/null

   Generally, it's polite to ask the owner of the RSS file if you can use
   their file, and also not to retrieve it more than once per hour.

The Image

   The image can be referenced in two ways::
<pre>
&lt;dtml-if "image.has_key(&#39;data&#39;)"&gt;
    &lt;img src="&dtml-absolute_url;/view_image"&gt;
&lt;/dtml-if&gt;
   or
&lt;dtml-var picture&gt;
</pre>

   The last convenience method will also put an anchor-tag around the img-tag
   if the RSS file contains a link for the image.

Textinput
The textinput could be used like this:
<pre>
&lt;dtml-with slashdot&gt;
&lt;form method="GET" action="&lt;dtml-var "textinput['link']"&gt;"&gt;
&lt;dtml-var "textinput['description']"&gt;&lt;br&gt;
&lt;dtml-var "textinput['title']"&gt;
&lt;input type="text" name="&lt;dtml-var "textinput['name']"&gt;"&gt;
&lt;/form&gt;
&lt;/dtml-with&gt;
</pre>

How it works

   An RDF Site Summary file consists of four main parts. A channel part,
   (inside &lt;channel&gt; tags), which is the description of the summary file
   itself. An optional image part, which contains a url to an image file
   of about 88x31 pixels. An optional textinput part. It contains the
   elements necessary to set up a search for the site you are retrieving
   the summary from. Finally there is the items-part. The first three are
   implemented as Python dictionaries called channel, image and
   textinput. The last one is implemented as an array of dictionaries.

   A Python dictionary is also known as an associative array. It is kind
   of like a sack, where you can put all your goodies tagged with a
   keyword you can use to get them back.

   RDFSummary parses the summary file, and for each tag inside the four
   main parts, it stores them under a keyword. Since there is only a few
   mandatory tags, you must typically first check if the dictionary
   contains the item before you can use it.

   RDFSummary supports the core RDF Site Summary, and the two modules:
   syndication and Dublin Core. How it supports them is very simple. It
   simply maps the namespaces to easily usable keywords. The Dublin Core
   has one tag for dates, but RDFSummary doesnt try to understand the
   date. It just treats it as a string.

Restrictions & peculiarities

   Encoding -- The encoding from the xml processing instruction is saved and
   added to the channel dictionary.

   HTML -- HTML (or XHTML) is not allowed inside an RDF file. This may
   come as surprise to some, but this would circumvent what RSS is
   trying to achieve.

   Entities -- All known and unknown entities are supported. If you look in
   the python code you'll see a list of browser-supported
   entities, but it is not used.

   Unknown tags -- RDFSummary does not know what to do with elements it
   doesn't know. You must add them to the 'known_elements' dictionary
   in RDFSummary.py

   Semantic augmentation -- Most of the RDF-elements expect just a
   simple text string. Sometimes this is not good enough. What if you
   want to provide an email address and phone number for the creator
   of a resource? The specification makes this possible by semantic
   augmentation. You just need to know that RDFSummary isn't able to
   handle semantic augmentation. You will get a syntax error.

Experimental support for events

   With version 1.4 I've add experimental support for the event RSS module,
   which I have authored myself and proposed to the
   "RSS-DEV":http://groups.yahoo.com/group/rss-dev working group. The event
   module will make it possible for you to grab events like meetings, conferences
   etc. from remote websites and create a calendar listed in the order of the
   event time.

Acknowledgements

   This product would probably never have seen the daylight if I hadn't
   been able to build on top of Edd Dumbill's SiteSummary product.
