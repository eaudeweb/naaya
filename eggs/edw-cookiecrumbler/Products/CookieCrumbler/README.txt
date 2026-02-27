CookieCrumbler lets you set up cookie-based authentication even
when your user folder does not support cookies.  Zope 2.3.x or
above is required.

To install: With Zope stopped, decompress the downloaded .tar.gz file
on your hard drive.  Place the CookieCrumbler directory in Zope's
Products directory.  Start Zope.  Using your brower, visit the
management interface.  Using the 'add' drop-down, add a CookieCrumbler
instance to your root folder.  (You may add it elsewhere if you want
to use cookie authentication only in a part of your site.)

If you ever have problems logging in because the CookieCrumbler is
getting in the way, add '?disable_cookie_login__=1' to the end of
the URL and you'll be able to use HTTP authentication again.

If CookieCrumbler gets in the way of WebDAV interactions, use a WebDAV
source port (see the Zope documentation.)

