Naaya Selenium Tests
====================

Install:
--------

1. install selenium grid from http://selenium-grid.seleniumhq.org/get_started.html

2. install ant using you system's packaging tool

3. get a copy of this repository in the ``src/`` folder and add it to the
   ``develop`` portion of the ``naaya.cfg``.

4. add ``naaya.selenium`` as an egg to ``zope-instance`` in ``naaya.cfg``.

5. run ``buildout``.

How to use:
-----------

1. When you write a test, you create a ``SeleniumTestCase`` subclass with
   ``test_*`` methods, just like in a normal ``unittest.testcase`` or
   ``NaayaTestCase`` scenario.

2. You **don't** need to explicitly create and load a ``TestSuite`` like it was done in
   ``unittest.testcase``. ``nynose`` does this explicitly via ``nose``.

3. By subclassing ``SeleniumTestCase`` you have access to the following methods:

   * ``login_user(user, password)``: logins a user in the selenium created browser.
     Valid users are listed in ``NaayaTestCase`` under ``portal_fixture``.
     Additionally, an administrator account is created by the
     ``NaayaPortalTestPlugin`` with username ``admin`` and empty password.

   * ``logout_user()``: logouts any logged-in user

4. In order to run the tests, you need to run ``ant launch-hub`` and ``ant
   launch-remote-control`` in selenium grid's directory. By default, they will
   use ports 4444 and 5555 but this can be changed.

5. The ``NaayaSeleniumTestPlugin`` (loaded at ``nynose``'s startup just like
   ``NaayaPortalTestPlugin``) will create a wsgi listener on a specific port
   and will serve all request coming from the selenium browser as if it was a
   Naaya site called ``portal``.

6. This plugin adds four options to ``nynose``:

   * ``--ny-selenium`` will enable selenium tests discovery and running. By default they are disabled.
   * ``--ny-instance-port`` will change wsgi listener's port
   * ``--selenium-grid-port`` will change selenium remote control port
   * ``--ny-selenium-browsers`` will change the browser used in testing

Example:
--------

Simply run the following command if defaults are ok::

	bin/nynose --ny-selenium naaya.selenium

To test with other Naaya modules (Products.Naaya for example) and change the
defaults (the instance port in this example) run::

	bin/nynose --ny-selenium --ny-instance-port=12345 naaya.selenium Products.Naaya

If you wish, you can run the selenium tests with ``naaya``::

	bin/nynose --ny-selenium naaya
