import flask
import sys
# https://github.com/maxcountryman/flask-login
# pip install flask-login
from flask.ext.login import LoginManager
import easypg
easypg.config_name = 'bookserver'

from lib import books, users


app = flask.Flask('BookServer')
app.secret_key = 'ItLWMzHsirkwfiiI9kIa'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_index'

# app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

# during developement
app.debug = True

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


@app.route("/")
def home_index():
    with easypg.cursor() as cur:
        book_info = books.get_spotlight_books(cur,4)
    return flask.render_template('home.html',
                                 books=book_info)

@app.route("/dashboard")
def user_dashboard():
    return flask.render_template('dashboard.html')

@app.route("/books")
def books_index():
    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        total_pages = books.get_total_pages(cur)

    with easypg.cursor() as cur:
        book_info = books.get_all_books(cur, page)

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1

    return flask.render_template('books.html',
                                 books=book_info,
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage)

@app.route("/reviews")
def reviews_index():
    #with easypg.cursor() as cur:
    #    narts = articles.get_article_count(cur)
    #    nproc, nser = proceedings.get_proceedings_stats(cur)
    #    stats = {'narticles': narts, 'nproceedings': nproc, 'nseries': nser}
    return flask.render_template('reviews.html')


@app.route("/user/<uid>")
def display_user(uid):
    # Other user's profile page
    raise NotImplementedError

@app.route("/user/login", methods=['GET', 'POST'])
def login_index():
    # Login page

    error = None
    if flask.request.method == 'POST':
        # login and validate the user...
        with easypg.cursor() as cur:

            login_status = users.validate_login(cur, flask.request.form['username'], flask.request.form['password'])
            if login_status > 0:
                user = User.get(login_status)
                try:
                    if flask.request.form['remeberLogin'] == "remeber-me":
                        remeber = True
                except KeyError:
                    remeber = False
                print "Rember: %s" % remeber
                print user.is_active
                flask.ext.login.login_user(user, remeber)
                flask.flash("Logged in successfully.")
                return flask.redirect(flask.request.args.get("next") or flask.url_for("home_index"))
            else:
                error = "Username or password not accepted."

    return flask.render_template("login.html", error=error)






@app.route("/user/logout")
@flask.ext.login.login_required
def logout():
    flask.ext.login.logout_user()
    flask.flash("You have been logged out!")
    return flask.redirect(flask.url_for('home_index'))

@app.route('/search')
def get_search_results():
    if 'q' in flask.request.args:
        query = flask.request.args['q']
    else:
        flask.abort(400)
    raise NotImplementedError

@app.route('/articles/<aid>/comments/add', methods=['POST'])
def add_comment(aid):
    name = flask.request.form['name']
    text = flask.request.form['comment']
    raise NotImplementedError
    app.logger.info('got comment from %s: %s', name, text)

    with easypg.cursor() as cur:
        articles.add_comment(cur, aid, name, text)
    # redirect user back to article which will display comments
    # always redirect after a POST
    return flask.redirect('/articles/' + aid)



class UserNotFoundError(Exception):
    pass



# Simple user class base on UserMixin
# http://flask-login.readthedocs.org/en/latest/_modules/flask/ext/login.html#UserMixin
class User():
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
                SELECT user_id, login_name, password
                FROM "user"
                WHERE user_id = %s
            ''', (id,))


            for id, login_name, password in cur:
                self.id = id
                self.name = login_name
                self.password = password

    @classmethod
    def get(self_class, id):
        '''Return user instance of id, return None if not exist'''
        try:
            return self_class(id)
        except UserNotFoundError:
            return None

    def __repr__(self):
        return '<User %r>' % (self.name)






if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

