import flask
# https://github.com/maxcountryman/flask-login
# pip install flask-login
from flask.ext.login import LoginManager
import easypg

from lib import books

easypg.config_name = 'bookserver'

import sys
reload(sys)
sys.setdefaultencoding('Cp1252')

app = flask.Flask('BookServer')
app.secret_key = 'ItLWMzHsirkwfiiI9kIa'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    if flask.request.method == 'POST':
        # login and validate the user...
        #login_user(user)
        flask.flash("Logged in successfully.")
        return flask.redirect(request.args.get("next") or url_for("index"))
    return flask.render_template("login.html")






@app.route("/user/logout")
def display_user_logout(request):
    # Logout page
    raise NotImplementedError

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
