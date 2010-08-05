# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2000-2004  Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


"""
This Zope product is a hotfix, it dynamically applies several patches
to Zope.
"""


# Import from Python
from gettext import GNUTranslations
import os
import pprint
from StringIO import StringIO as originalStringIO
from thread import get_ident, allocate_lock
from types import UnicodeType

# Import from itools
from itools import get_abspath
from itools.i18n.accept import AcceptCharset, AcceptLanguage
from itools.zope.Context import Context
from itools.zope import get_context

# Import Zope modules
import Globals
from Products.PageTemplates.PageTemplate import getEngine, PageTemplate, \
     PTRuntimeError
from Products.PageTemplates import TALES
from TAL.TALInterpreter import TALInterpreter
from zLOG import LOG, ERROR, INFO, PROBLEM, DEBUG
from ZPublisher import Publish, mapply
from ZPublisher.HTTPRequest import HTTPRequest

# Flag
patch = False
Z_DEBUG_MODE = os.environ.get('Z_DEBUG_MODE') == '1'

# PATCH 1: Global Request
#
# The original purpose was to get the request object from places where the
# acquisition was disabled (within the __of__ method for example). It was
# inspired by the Tim McLaughlin's GlobalGetRequest proposal, see
# http://dev.zope.org/Wikis/DevSite/Proposals/GlobalGetRequest
#
# Currently it keeps a Context instance, which wraps the request object,
# but also other things, like the user's session, as it is required by
# the ikaaro CMS.
#
# The context objects are stored in a dictionary in the Publish module,
# whose keys are the thread id.
#
# Also, we keep the get_request method in the Globals module for backwards
# compatibility (with TranslationService for example).

contexts = {}
_the_lock = allocate_lock()


def new_publish(zope_request, module_name, after_list, debug=0):
    # Build the Context instance, a wrapper around the Zope request
    context = Context(zope_request)
    # Store it
    id = get_ident()
    _the_lock.acquire()
    try:
        contexts[id] = context
    finally:
        _the_lock.release()

    try:
        # Publish
        x = Publish.zope_publish(zope_request, module_name, after_list, debug)
    finally:
        # Remove the context object.
        # When conflicts occur the "publish" method is called again,
        # recursively. In this situation the context dictionary would
        # be cleaned in the innermost call, hence outer calls find the
        # context does not exists anymore. For this reason we check first
        # wether the context is there or not.
        if id in contexts:
            _the_lock.acquire()
            try:
                del contexts[id]
            finally:
                _the_lock.release()

    return x


if patch is False:
    # XXX What happens when Localizer 1.0 and iHotfix are installed??
    # Apply the patch
    Publish.zope_publish = Publish.publish
    Publish.publish = new_publish

    # First import (it's not a refresh operation).
    # We need to apply the patches.
    patch = True

    # Add get_request for backwards compatibility
    def get_request():
        return get_context().request.zope_request
    Globals.get_request = get_request



# PATCH 2: Accept
#
# Adds the variables AcceptLanguage and AcceptCharset to the REQUEST.
# They provide a higher level interface than HTTP_ACCEPT_LANGUAGE and
# HTTP_ACCEPT_CHARSET.

# Apply the patch
def new_processInputs(self):
    HTTPRequest.old_processInputs(self)

    request = self

    # Set the AcceptCharset variable
    accept = request['HTTP_ACCEPT_CHARSET']
    self.other['AcceptCharset'] = AcceptCharset(request['HTTP_ACCEPT_CHARSET'])

    # Set the AcceptLanguage variable
    # Initialize with the browser configuration
    accept_language = request['HTTP_ACCEPT_LANGUAGE']
    # Patches for user agents that don't support correctly the protocol
    user_agent = request['HTTP_USER_AGENT']
    if user_agent.startswith('Mozilla/4') and user_agent.find('MSIE') == -1:
        # Netscape 4.x
        q = 1.0
        langs = []
        for lang in [ x.strip() for x in accept_language.split(',') ]:
            langs.append('%s;q=%f' % (lang, q))
            q = q/2
        accept_language = ','.join(langs)

    accept_language = AcceptLanguage(accept_language)

    self.other['AcceptLanguage'] = accept_language
    # XXX For backwards compatibility
    self.other['USER_PREF_LANGUAGES'] = accept_language


if patch:
##    from ZPublisher.BaseRequest import BaseRequest
##    from itools.zope.request import iRequest

##    HTTPRequest.__bases__ = (iRequest, BaseRequest)

    HTTPRequest.old_processInputs = HTTPRequest.processInputs
    HTTPRequest.processInputs = new_processInputs



# PATCH 3: Unicode
#
# Enables support of Unicode in ZPT.
# For Zope 2.5.1 (unsupported), patch appropriately.
# For Zope 2.6b1+
#   - if LOCALIZER_USE_ZOPE_UNICODE, use standard Zope Unicode handling,
#   - otherwise use iHotfix's version of StringIO for ZPT and TAL.

patch_251 = not hasattr(TALInterpreter, 'StringIO')

if patch_251:
    try:
        # Patched 2.5.1 should have ustr in __builtins__
        ustr
    except NameError:
        LOG('iHotfix', PROBLEM,
            'A Unicode-aware version of Zope is needed by iHotfix to'
            ' apply its Unicode patch. Please consult the documentation'
            ' for a patched version of Zope 2.5.1, or use Zope 2.6b1 or'
            ' later.')
    else:
        # 3.1 - Fix two instances where ustr must be used
        def evaluateText(self, expr):
            text = self.evaluate(expr)
            if text is TALES.Default or text is None:
                return text
            return ustr(text) # Use "ustr" instead of "str"
        TALES.Context.evaluateText = evaluateText

        def do_insertStructure_tal(self, (expr, repldict, block)):
            structure = self.engine.evaluateStructure(expr)
            if structure is None:
                return
            if structure is self.Default:
                self.interpret(block)
                return
            text = ustr(structure)  # Use "ustr" instead of "str"
            if not (repldict or self.strictinsert):
                # Take a shortcut, no error checking
                self.stream_write(text)
                return
            if self.html:
                self.insertHTMLStructure(text, repldict)
            else:
                self.insertXMLStructure(text, repldict)
        TALInterpreter.do_insertStructure_tal = do_insertStructure_tal
        TALInterpreter.bytecode_handlers_tal["insertStructure"] = do_insertStructure_tal


# 3.2 - Fix uses of StringIO with a Unicode-aware StringIO

class iHotfixStringIO(originalStringIO):
    def write(self, s):
        if isinstance(s, UnicodeType):
            response = get_request().RESPONSE
            try:
                s = response._encode_unicode(s)
            except AttributeError:
                # not an HTTPResponse
                pass
        originalStringIO.write(self, s)


if not patch_251:
    if os.environ.get('LOCALIZER_USE_ZOPE_UNICODE'):
        LOG('iHotfix', DEBUG, 'No Unicode patching')
        # Use the standard Zope way of dealing with Unicode
    else:
        LOG('iHotfix', DEBUG, 'Unicode patching for Zope 2.6b1+')
        # Patch the StringIO method of TALInterpreter and PageTemplate
        def patchedStringIO(self):
            return iHotfixStringIO()
        TALInterpreter.StringIO = patchedStringIO
        PageTemplate.StringIO = patchedStringIO

else:
    LOG('iHotfix', DEBUG, 'Unicode patching for Zope 2.5.1')
    # Patch uses of StringIO in Zope 2.5.1
    def no_tag(self, start, program):
        state = self.saveState()
        self.stream = stream = iHotfixStringIO()
        self._stream_write = stream.write
        self.interpret(start)
        self.restoreOutputState(state)
        self.interpret(program)
    TALInterpreter.no_tag = no_tag

    def do_onError_tal(self, (block, handler)):
        state = self.saveState()
        self.stream = stream = iHotfixStringIO()
        self._stream_write = stream.write
        try:
            self.interpret(block)
        except self.TALESError, err:
            self.restoreState(state)
            engine = self.engine
            engine.beginScope()
            err.lineno, err.offset = self.position
            engine.setLocal('error', err)
            try:
                self.interpret(handler)
            finally:
                err.takeTraceback()
                engine.endScope()
        else:
            self.restoreOutputState(state)
            self.stream_write(stream.getvalue())
    TALInterpreter.do_onError_tal = do_onError_tal

    def pt_render(self, source=0, extra_context={}):
        """Render this Page Template"""
        if self._v_errors:
            raise PTRuntimeError, 'Page Template %s has errors.' % self.id
        output = iHotfixStringIO()
        c = self.pt_getContext()
        c.update(extra_context)
        if Z_DEBUG_MODE:
            __traceback_info__ = pprint.pformat(c)

        TALInterpreter(self._v_program, self._v_macros,
                       getEngine().getContext(c),
                       output,
                       tal=not source, strictinsert=0)()
        return output.getvalue()
    PageTemplate.pt_render = pt_render

del patch_251



# PATCH 4: mxDateTime
#
# Help to use the mx.DateTime Python module from restricted code.

try:
    from mx import DateTime
except ImportError:
    pass
else:
    # Define a helper method that should be provided by Zope
    from AccessControl.SimpleObjectPolicies import ContainerAssertions
    def allow_type(ob):
        """
        Allows a simple object to be used from restricted code.
        """
        ContainerAssertions[type(ob)] = 1


    # Allow access to DateTime instances from restricted code
    allow_type(DateTime.today())

    # XXX Remains to let access to other object types (DateTimeDelta, etc.)

    # Allow access to the DateTime module
    DateTime.__allow_access_to_unprotected_subobjects__ = 1

    # Puts the mxDateTime module in the '_' variable
    # XXX Perhaps we should put the whole mx module.
    from DocumentTemplate.cDocumentTemplate import TemplateDict
    TemplateDict.mxDateTime = DateTime



# PATCH 5: locale
#
# Actually, this is not a patch. It provides an API to access translations
# stored as MO files in the 'locale' directory. This code has been moved
# from Localizer.

# {<locale directory>: {<language code>: <GNUTranslations instance>}}
translations = {}

def get_translations(localedir, language=None):
    """
    Looks the <language>.mo file in <localedir> and returns a
    GNUTranslations instance for it. If <language> is None uses
    the language negotiator to guess the user preferred language.
    """
    # Initialize the product translations
    locale = localedir
    if not translations.has_key(locale):
        translations[locale] = None

    if translations[locale] is None:
        translations[locale] = {}
        # Load .mo files
        for filename in [ x for x in os.listdir(locale) if x.endswith('.mo') ]:
            lang = filename[:-3]
            filename = os.path.join(locale, filename)
            f = open(filename, 'rb')
            translations[locale][lang] = GNUTranslations(f)
            f.close()

    # Get the translations to use
    ptranslations = translations[locale]

    if language is None:
        context = get_context()
        # Build the list of available languages
        available_languages = ptranslations.keys()
        # Get the language!
        accept = context.request.accept_language
        lang = accept.select_language(available_languages)
    else:
        lang = None

    return ptranslations.get(lang or language, None)



def gettext(self, message, language=None):
    """ """
    # Get the translations to use
    translations = get_translations(self.locale, language)

    if translations is not None:
        return translations.ugettext(message)

    return message



class translation:
    def __init__(self, namespace):
        self.locale = get_abspath(namespace, 'locale/')

    __call__ = gettext



def N_(message, language=None):
    """
    Used to markup a string for translation but without translating it,
    this is known as deferred translations.
    """
    return message


# XXX For backwards compatibility.
dummy = N_
