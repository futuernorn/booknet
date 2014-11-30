import flask
import sys
# https://github.com/maxcountryman/flask-login
# pip install flask-login
from flask.ext.login import LoginManager
import easypg
easypg.config_name = 'bookserver'
import re
from lib import books, reviews, users


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
        review_info = reviews.get_spotlight_reviews(cur,4)
    return flask.render_template('home.html',
                                 books=book_info,
                                 reviews=review_info)

@app.route("/dashboard")
def user_dashboard():
    return flask.render_template('dashboard.html')

@app.route("/users")
def users_index():
    if 'sorting' in flask.request.args:
        sorting = flask.request.args['sorting']
    else:
        sorting = None
    if 'sort_direction' in flask.request.args:
        sort_direction = flask.request.args['sort_direction']
    else:
        sort_direction = None

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        total_pages = users.get_total_pages(cur)

    with easypg.cursor() as cur:
        user_info = users.get_all_users(cur, page, flask.session['user_id'])

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1

    return flask.render_template('users.html',
                                 users=user_info,
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage)
@app.route("/profile")
def current_user_profile():
    return NotImplementedError
@app.route("/user/<uid>")
def user_profile(uid):
    selected_user = User.get(uid)
    user_info = None
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")
    return flask.render_template('profile.html',
                                 user_id=uid,
                                 selected_user=selected_user,
                                 user_info = user_info,
                                 next=next)

@app.route("/list/add/book")
def add_book_list():
    raise NotImplementedError

@app.route("/books/author")
def books_by_author():
    raise NotImplementedError
@app.route("/books/publisher")
def books_by_publisher():
    raise NotImplementedError

@app.route("/books/subject")
def books_by_subjects():
    raise NotImplementedError

@app.route("/books/subject/<subject>")
def books_by_subject(subject):
    raise NotImplementedError

@app.route("/books/<bid>")
def display_book(bid):
    with easypg.cursor() as cur:
        book_info = books.get_book(cur,bid)
    # print book_info
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")
    return flask.render_template("book.html",
                                 book_info=book_info,
                                 next=next)
@app.route("/book/edit/<bid>")
def edit_book(bid):
    with easypg.cursor() as cur:
        book_info = books.get_book(cur,bid)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("display_book", bid=bid)
    # book_info['authors'].append("Test 1")
    # book_info['authors'].append("Test 2")
    # book_info['authors'].append("Test 3")
    # book_info['authors'].append("Test 4")
    # book_info['author_count'] = 4
    return flask.render_template("book_edit_form.html",
                                 book_info=book_info,
                                 next=next)

@app.route("/books")
def books_index():


    if 'sorting' in flask.request.args:
        sorting = flask.request.args['sorting']
    else:
        sorting = None
    if 'sort_direction' in flask.request.args:
        sort_direction = flask.request.args['sort_direction']
    else:
        sort_direction = None

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        total_pages = books.get_total_pages(cur)

    with easypg.cursor() as cur:
        if current_user.is_authenticated():
            book_info = books.get_all_books(cur, page, flask.session['user_id'], sorting, sort_direction)
        else:
            book_info = books.get_all_books(cur, page, None, sorting, sort_direction)

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
                                 prevPage=prevPage,
                                 sorting=sorting,
                                 sort_direction=sort_direction)

@app.route("/books/log/add", methods=['POST'])
def add_reading_log():
    raise NotImplementedError
    return redirect(request.args.get("next") or url_for("books_index"))


@app.route("/books/rating/add", methods=['POST'])
def add_book_rating():
    rating = flask.request.form['rating']
    book_id = flask.request.form['book_id']
    # print flask.request.form
    user_id = flask.request.form['user_id']
    user = User.get(user_id)
    with easypg.cursor() as cur:
        message = books.add_rating(cur, book_id, rating, user_id)

    flask.flash(message)
    if flask.request.form['next']:
        return flask.redirect(flask.request.form['next'])

    return flask.redirect(flask.url_for('books_index'))

@app.route("/books/rating/remove/<bid>")
def remove_book_rating(bid):
    # raise NotImplementedError
    book_id = bid
    if current_user.is_authenticated():
        user_id = flask.session['user_id']
    else:
        user_id = None
    

    
    
    with easypg.cursor() as cur:
        message = books.remove_rating(cur, book_id, user_id)

    flask.flash(message)
    return flask.redirect(flask.url_for('books_index'))

@app.route("/reviews/book/<bid>")
def display_reviews_for_book(bid):
    raise NotImplementedError
@app.route("/reviews/<rid>")
def display_review(rid):
    review_info = None

    return flask.redirect("review.html",
                          review_info=review_info)

@app.route("/reviews/add/<bid>", methods=['GET', 'POST'])
@flask.ext.login.login_required
def add_review(bid):
    errors = []
    if flask.request.method == 'POST':
        raise NotImplementedError
    with easypg.cursor() as cur:
        book_info = books.get_book(cur,bid)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")
    return flask.render_template("review_add_form.html",
                                 book_info = book_info,
                                 next=next)

@app.route("/list")
def lists_index():
    return flask.render_template("lists_list.html")

@app.route("/reviews")
def reviews_index():
    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        total_pages = reviews.get_total_pages(cur)

    with easypg.cursor() as cur:
        review_info = reviews.get_all_reviews(cur, page)

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1

    return flask.render_template('review_list.html',
                                 reviews=review_info,
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage)



@app.route("/user/<uid>")
def display_user(uid):
    # Other user's profile page
    raise NotImplementedError

@app.route("/user/login", methods=['GET', 'POST'])
def login_index():
    # Login page

    errors = []
    if flask.request.method == 'POST':
        # login and validate the user...
        with easypg.cursor() as cur:

            login_status = users.validate_login(cur, flask.request.form)
            if login_status > 0:
                user = User.get(login_status)
                try:
                    if flask.request.form['remeberLogin'] == "remeber-me":
                        remember = True
                except KeyError:
                    remember = False
                print user.is_active
                flask.ext.login.login_user(user, remember)
                flask.flash("Logged in successfully.")
                return flask.redirect(flask.request.args.get("next") or flask.url_for("home_index"))
            else:
                errors.append("Username or password not accepted.")

    return flask.render_template("login.html", errors=errors)

@app.route("/user/register", methods=['GET', 'POST'])
def register_index():
    errors = []
    if flask.request.method == 'POST':
        if flask.request.form['password'] != flask.request.form['password_confirm']:
            errors.append("Passwords do not match!")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", flask.request.form['email']):
            # KISS here, just confirm one @ sign, period after @ sign; no confirmation address is active
            # from: http://stackoverflow.com/a/8022584/1431509
            errors.append("Email address not valid!")
        else:
            with easypg.cursor() as cur:

                register_status, id, message = users.register_user(cur, flask.request.form)

                if register_status:
                    user = User.get(id)
                    try:
                        if flask.request.form['remeberLogin'] == "remeber-me":
                            remember = True
                    except KeyError:
                        remember = False
                    flask.ext.login.login_user(user, remember)
                    flask.flash("Registered and Logged in successfully.")
                    flask.flash("Good to meet you %s!" % flask.request.form['username'])
                else:
                    errors.append(message)


    return flask.render_template("register.html", errors=errors)




@app.route("/user/logout")
@flask.ext.login.login_required
def logout():
    flask.ext.login.logout_user()
    flask.flash("You have been logged out!")
    return flask.redirect(flask.url_for('home_index'))

@app.route('/search')
def search_index():
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

