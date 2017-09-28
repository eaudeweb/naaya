from random import randint

class SessionManager(object):
    SESSION_KEY = '__naaya_observatory_session'

    def generate_session_key(self):
        return randint(10**5, 10**10)

    def set_session(self, REQUEST):
        author = REQUEST.AUTHENTICATED_USER.getUserName()
        if author == 'Anonymous User':
            session_key = REQUEST.cookies.get(self.SESSION_KEY, None)
            if session_key == None:
                session_key = self.generate_session_key()
                REQUEST.RESPONSE.setCookie(self.SESSION_KEY, session_key)
            return session_key

    def get_author_and_session(self, REQUEST):
        author = REQUEST.AUTHENTICATED_USER.getUserName()
        if author == 'Anonymous User':
            session_key = REQUEST.cookies.get(self.SESSION_KEY)
        else:
            session_key = None
        return author, session_key

