"""

Authors: Victor Szczepanski

"""

# System Imports
import os
import cherrypy
from cherrypy.lib.static import serve_file
from sqlalchemy.orm.exc import NoResultFound

# Local Imports
from sessionManager import sessionScope
from models import User

SESSION_KEY = '_cp_username'
PATH = os.path.abspath(os.path.dirname(__file__))


def check_credentials(username, password, session):
    """
    Verifies credentials for username and password.
    :returns: None on success or a string describing the error on failure
    """

    try:
        user = session.query(User).filter_by(email=username, password=password).one()
    except NoResultFound:
        return "Incorrect username or password"

    return None


def check_auth(*args, **kwargs):
    """
    A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill
    """
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")


cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)


def require(*conditions):
    """
    A decorator that appends conditions to the auth.require config variable.

    Conditions are callables that return True
    if the user fulfills the conditions they define, False otherwise

    They can access the current username as cherrypy.request.login

    Define those at will however suits the application.
    """
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check


def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy


def any_of(*conditions):

    # :returns: True if any of the conditions match

    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check


def all_of(*conditions):
    """
    :returns: True if all of the conditions match.

    By default all conditions are required, but this might still be
    needed if you want to use it inside of an any_of(...) condition
    """
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


class AuthController(object):

    # Controller to provide login and logout actions.

    def on_login(self, username):
        # Called on successful login
        pass

    def on_logout(self, username):
        # Called on logout
        pass

    def loginForm(self, username, msg="Enter login information", from_page="/"):
        return serve_file(PATH + '/login.html', content_type="text/html")

    @cherrypy.expose
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.loginForm("", from_page=from_page)

        with sessionScope() as s:
            error_msg = check_credentials(username, password, s)

        if error_msg:
            return self.loginForm(username, error_msg, from_page)
        else:
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")

    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(from_page or "/")
