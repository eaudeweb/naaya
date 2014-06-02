NyBFile - NyFile that uses ZODB BLOB
====================================

To use NyBFile remember to add `blob-storage` path to your zope instance. Also
if you have multiple instances (ZEO+pound) use shared-blob = on to share the
same files for different instances.

Example::

	shared-blob = on
	blob-storage = ${buildout:directory}/var/blobstorage
