Sending e-mail
==============

Naaya can send e-mail in one of two ways: directly, or using a mail queue.

Direct sending
--------------
Each portal can be configured to send mail by itself. SMTP connection details
need to be entered in :ref:`admin-portal-properties`, and by default new
portals will use localhost on port 25. If no connection details are configured,
and no queue (see below) was registered, email messages will not be sent at
all.

Mail queue
----------
For handling large amounts of email, direct delivery is not recommended, since
it blocks the page loading until all messages are sent. Instead, messages can
be written to a queue on disk in Maildir format, and a daemon process sends
them asynchronously.

To configure a mail queue folder, set the NAAYA_MAIL_QUEUE environment variable
in the buildout file::

    environment-vars =
        NAAYA_MAIL_QUEUE ${buildout:directory}/var/mail-queue

Then, set up a mailer daemon, that will poll the queue every few seconds and
send any messages it finds. For instance, the following is a buildout part
that generates a script ``bin/mail-sender``::

    [mail-sender]
    recipe = zc.recipe.egg
    eggs = repoze.sendmail
    scripts = qp=mail-sender

And run the script::

    bin/mail-sender --daemon var/mail-queue
