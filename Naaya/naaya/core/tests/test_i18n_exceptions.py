import unittest

from naaya.core.exceptions import i18n_exception, localize_exc

class I18nExceptionsTest(unittest.TestCase):
    def test_exception_with_i18n(self):
        err = i18n_exception(ValueError, "my local message")
        assert isinstance(err, ValueError)
        assert err.args == ("my local message",)
        assert str(err) == "my local message"
        assert hasattr(err, "_ny_i18n")
        assert err._ny_i18n == ("my local message", {})

        err2 = i18n_exception(IndexError, "bad index for ${name}", name="joe")
        assert isinstance(err2, IndexError)
        assert err2.args == ("bad index for joe",)
        assert str(err2) == "bad index for joe"
        assert hasattr(err2, "_ny_i18n")
        assert err2._ny_i18n == ("bad index for ${name}", {'name': 'joe'})

    def test_localize_exception(self):
        message_catalog = {
            'bad ${name}': 'TRANSLATED ${name} BLAH',
            'hello world': 'howdy world',
            'blah blah': 'yada yada',
        }
        gettext = message_catalog.get

        e1 = ValueError("hello world")
        assert localize_exc(e1, gettext) == "howdy world"

        e2 = i18n_exception(ValueError, "blah blah")
        assert localize_exc(e2, gettext) == "yada yada"

        e3 = i18n_exception(ValueError, "bad ${name}", name="llama")
        assert localize_exc(e3, gettext) == "TRANSLATED llama BLAH"
