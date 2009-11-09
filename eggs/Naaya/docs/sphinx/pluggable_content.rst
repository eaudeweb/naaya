Pluggable content
=================

Initial setup
-------------

Content types may want to perform some operations when first installed (e.g.
setting permissions, creating portlets, etc). They should implement a setup
callback and register its reference in the content's config dict as
`config['setup']`.
