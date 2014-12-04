__author__ = 'Jeffrey Hogan'
from flask.ext.login import UserMixin
import easypg
easypg.config_name = 'bookserver'

class UserNotFoundError(Exception):
    pass

# Simple user class base on UserMixin
# http://flask-login.readthedocs.org/en/latest/_modules/flask/ext/login.html#UserMixin
class BooknetUser(UserMixin):
    '''
    This provides default implementations for the methods that Flask-Login
    expects user objects to have.
    '''

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __init__(self, id):
        with easypg.cursor() as cur:
            cur.execute('''
                SELECT user_id, login_name, password, level_id
                FROM booknet_user
                WHERE user_id = %s
            ''', (id,))


            for id, login_name, password, level_id in cur:
                self.id = id
                self.name = login_name
                self.password = password
                self.access_level = level_id

    @classmethod
    def get(self_class, id):
        '''Return user instance of id, return None if not exist'''
        try:
            return self_class(id)
        except UserNotFoundError:
            return None

    def __repr__(self):
        return '<User %r>' % (self.name)