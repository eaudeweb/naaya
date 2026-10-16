naaya.sentry
============

Sends Zope publishing errors and logged errors to Sentry. Ported from the
Zope parts of eea.sentry 3.2.

At Zope startup ``sentry_sdk`` is initialised when ``SENTRY_DSN`` is set. A
subscriber to ``IPubFailure`` reports each publishing error with the request
data (form, request headers, lazy items, other), the user, the browser and
the site id. Exceptions listed as ignored in the site's ``error_log`` are not
sent.

Environment variables
---------------------

``SENTRY_DSN``
    Sentry DSN; Sentry stays disabled when it is empty or unset.
``SENTRY_ENVIRONMENT``
    Sentry environment, default ``devel``.
``SENTRY_RELEASE``
    Release name, falls back to ``EEA_KGS_VERSION``, then ``dev``.
``SENTRY_SITE``
    ``site`` tag when no Naaya site is found for the request, falls back to
    ``SERVER_NAME``, then ``dev``.

Buildout
--------

Add ``naaya.sentry`` and ``sentry-sdk`` to the instance ``eggs`` and
``naaya.sentry`` to ``zcml``.
