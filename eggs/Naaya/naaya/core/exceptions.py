""" Naaya core exceptions """

def i18n_exception(cls, msg, **params):
    """
    Construct an exception with i18n data attached::
      >>> e = i18n_exception(ValueError, "it broke")
      ValueError('it broke',)
      >>> e = i18n_exception(ValueError, "it broke ${how}", how="badly)
      ValueError('it broke badly',)

    Typical usage:
      >>> raise i18n_exception(ValueError, "it broke ${how}", how="badly)
      ...
      ValueError: "it broke badly"

    The exception can be localized with :func:`localize_exc`.
    """
    formatted_msg = msg
    for name, value in params.iteritems():
        formatted_msg = formatted_msg.replace('${%s}' % name, value)

    exc = cls(formatted_msg)
    exc._ny_i18n = (msg, params)

    return exc

def localize_exc(exc, gettext):
    """
    Localize a given exception using the translation tool ``gettext``. If the
    exception was constructed with i18n_exception, then localize_exc is aware
    of variable substitutions, and will translate them properly.
    """
    assert isinstance(exc, Exception)

    try:
        msg, params = exc._ny_i18n
    except AttributeError:
        msg = str(exc)
        params = {}

    msg = gettext(msg)
    for name, value in params.iteritems():
        msg = msg.replace('${%s}' % name, value)

    return msg

class ValidationError(Exception):
    """Used for signaling errors in HTML form validation

    """
