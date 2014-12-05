import flask
import sys
# https://github.com/maxcountryman/flask-login
# pip install flask-login
from flask.ext.login import LoginManager
import easypg
easypg.config_name = 'bookserver'
import re
from BooknetUser import *
from lib import books, reviews, users, lists, logs

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

ITEMS_PER_PAGE = 15

########################## Login Manager / Session Control ######################
app = flask.Flask('BookServer')
app.secret_key = 'ItLWMzHsirkwfiiI9kIa'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_index'


@login_manager.user_loader
def load_user(userid):
    return BooknetUser.get(userid)

# during developement
app.debug = True

######################### Main Index / Home #################################
@app.route("/")
def home_index():
    with easypg.cursor() as cur:
        pages, book_info = books.get_spotlight_books(cur,4)
        pages, review_info = reviews.get_spotlight_reviews(cur,4)
        list_info = lists.get_spotlight_lists(cur,4)
    return flask.render_template('home.html',
                                 books=book_info,
                                 reviews=review_info,
                                 lists=list_info)




######################## Books #########################################################################################

# Author ##############################
@app.route("/books/authors")
def books_by_authors():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, book_info = books.get_books_by_authors(cur, start, limit, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, book_info = books.get_books_by_authors(cur, start, limit, None, sorting, sort_direction)

    if sorting:
        parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    else:
        parameters = ''


    sort_options = {"Author Name": "author_name", "Avg. Rating": "avg_rating", "# Pages": "num_pages", "# Books": "num_books"}
    return render_books_index('books_by_authors.html', book_info, total_pages, sort_options, parameters, 'Books By Authors')

@app.route("/author/<author_name>")
def display_author(author_name):
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, author_info = books.get_books_by_author(cur, start, limit, author_name, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, author_info = books.get_books_by_author(cur, start, limit, author_name, None, sorting, sort_direction)

    sort_options = {"Title": "book_title", "Publication Date": "publication_date", "Avg. Rating": "avg_rating",
                    "Number of Readers": "num_readers"}
    parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    return render_books_index('author.html', author_info, total_pages, sort_options, parameters, 'Books - %s' % author_name)

# Publisher ###########################
@app.route("/books/publishers")
def books_by_publishers():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)

    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, publisher_info = books.get_books_by_publishers(cur, start, limit, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, publisher_info = books.get_books_by_publishers(cur, start, limit, None, sorting, sort_direction)

    if sorting:
        parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    else:
        parameters = ''


    sort_options = {"Publisher": "publisher_name", "Avg. Rating": "avg_rating", "# Pages": "num_pages", "# Books": "num_books"}
    return render_books_index('books_by_publishers.html', publisher_info, total_pages, sort_options, parameters, 'Books By Publishers')



@app.route("/publisher/<pid>")
def display_publisher(pid):
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, publisher_info = books.get_books_by_publisher(cur, start, limit, pid, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, publisher_info = books.get_books_by_publisher(cur, start, limit, pid, None, sorting, sort_direction)

    sort_options = {"Title": "book_title", "Publication Date": "publication_date", "Avg. Rating": "avg_rating",
                    "Number of Readers": "num_readers"}
    if sorting:
        parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    else:
        parameters = ''
    return render_books_index('author.html', publisher_info, total_pages, sort_options, parameters, 'Books - %s' % publisher_info['name'])

# Subject #############################
@app.route("/books/subjects")
def books_by_subjects():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, book_info = books.get_books_by_subjects(cur, start, limit, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, book_info = books.get_books_by_subjects(cur, start, limit, None, sorting, sort_direction)

    if sorting:
        parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    else:
        parameters = ''


    sort_options = {"Subject": "subject_name", "Avg. Rating": "avg_rating", "# Pages": "num_pages", "# Books": "num_books"}
    return render_books_index('books_by_subjects.html', book_info, total_pages, sort_options, parameters, 'Books By Subjects')

@app.route("/books/subject/<subject>")
def books_by_subject(subject):
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, book_info = books.get_books_by_subject(cur, start, limit, subject, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, book_info = books.get_books_by_subject(cur, start, limit, subject, None, sorting, sort_direction)

    sort_options = {"Title": "book_title", "Publication Date": "publication_date", "Avg. Rating": "avg_rating",
                    "Number of Readers": "num_readers"}
    parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    
    return render_books_index('books_index.html', book_info, total_pages, sort_options, parameters, 'Books - %s' % subject)

@app.route("/books/<bid>")
def display_book(bid):
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            book_info = books.get_book(cur,bid,flask.ext.login.current_user.id)
        else:
            book_info = books.get_book(cur,bid)
    # print book_info
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")
    return flask.render_template("book.html",
                                 book_info=book_info,
                                 next=next)



@app.route("/books")
def books_index():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, book_info = books.get_books(cur, start, limit, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, book_info = books.get_books(cur, start, limit, None, sorting, sort_direction)

    if sorting:
        parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    else:
        parameters = ''
    sort_options = {"Title": "book_title", "Publication Date": "publication_date", "Avg. Rating": "avg_rating",
                    "Number of Readers": "num_readers"}
    return render_books_index('books_index.html',book_info, total_pages, sort_options, parameters)

@app.route("/books/covers")
def display_books_with_covers():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, publisher_info = books.get_books_with_covers(cur, start, limit, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, publisher_info = books.get_books_with_covers(cur, start, limit, None, sorting, sort_direction)

    sort_options = {"Title": "book_title", "Publication Date": "publication_date", "Avg. Rating": "avg_rating",
                    "Number of Readers": "num_readers"}
    if sorting:
        parameters = "&sorting=%s&sort_direction=%s" % (sorting, sort_direction)
    else:
        parameters = ''
    return render_books_index('books_index.html', publisher_info, total_pages, sort_options, parameters, 'Books With Covers')

def parse_sorting():
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

    return page, sorting, sort_direction

def render_books_index(template, data, total_pages, sort_options = None, parameters = None, title='Books'):
    page, sorting, sort_direction = parse_sorting()
    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1


    return flask.render_template(template,
                                 data=data,
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage,
                                 sorting=sorting,
                                 sort_direction=sort_direction,
                                 sort_options=sort_options,
                                 parameters=parameters,
                                 page_title=title)

# Modify #######################
@app.route("/book/add", methods=['GET', 'POST'])
@flask.ext.login.login_required
def add_book_core():
    return add_book(0)

@app.route("/book/add/<bid>", methods=['GET', 'POST'])
@flask.ext.login.login_required
def add_book(bid):
    errors = []
    if flask.request.method == 'POST':
        with easypg.cursor() as cur:
            edit_status, messages, book_id = books.add_book(cur, bid, flask.ext.login.current_user.id, flask.request.form)
            print "Posted book data: %s..." % messages
            if edit_status:
                for message in messages:
                    flask.flash(message)
                return flask.redirect(flask.request.args.get("next") or flask.url_for("display_book", bid=book_id))
            else:
                for message in messages:
                    errors.append(message)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")

    book_info = {'title': 'New Book Addition', 'core_id': '0'}
    return flask.render_template("book_edit_form.html",
                                 book_info=book_info,
                                 page_title="Add A Book!",
                                 error=errors,
                                 next=next)


@app.route("/book/edit/<bid>", methods=['GET', 'POST'])
def edit_book(bid):
    errors = []
    if flask.request.method == 'POST':
        with easypg.cursor() as cur:
            edit_status, messages = books.edit_book(cur, bid, flask.request.form)
            if edit_status:
                for message in messages:
                    flask.flash(message)
                return flask.redirect(flask.request.args.get("next") or flask.url_for("display_book", bid=bid))
            else:
                for message in messages:
                    errors.append(message)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("display_book", bid=bid)
    with easypg.cursor() as cur:
            book_info = books.get_book(cur,bid)
    return flask.render_template("book_edit_form.html",
                                 book_info=book_info,
                                 error=errors,
                                 next=next)

#################### Reading Logs ######################################################################################

@app.route("/log/<lid>")
def display_log(lid):
    with easypg.cursor() as cur:
        log_info = logs.get_log(cur, lid)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")
    return flask.render_template("log.html",
                          log=log_info,
                          next=next)

@app.route("/log/<year>")
def display_logs_by_year(year):
    raise NotImplementedError


@app.route("/books/log/add", methods=['POST'])
@flask.ext.login.login_required
def add_reading_log():
    errors = []

    app.logger.info('Received new data for log from user_id %s: %s', flask.ext.login.current_user.id, flask.request.form)
    with easypg.cursor() as cur:
        entry_status, messages, log_id = books.add_log(cur, flask.ext.login.current_user.id, flask.request.form)
        app.logger.info("Log submitted %s - %s - %s", entry_status, messages, log_id)
        if entry_status:
            for message in messages:
                flask.flash(message)
            return flask.redirect(flask.request.args.get("next") or flask.url_for("display_log", lid=log_id))
        else:
            for message in messages:
                errors.append(message)


    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("books_index")

    return flask.redirect(next)

@app.route("/log/_current_user/<bid>")
@flask.ext.login.login_required
def get_user_logs(bid):
    user_id = flask.ext.login.current_user.id
    with easypg.cursor() as cur:
        user_lists = users.get_user_logs(cur, user_id, bid)
    return flask.jsonify(user_lists)



####################### Lists ##########################################################################################

@app.route("/list/add/bid", methods=['POST'])
@flask.ext.login.login_required
def add_book_list():
    errors = []

    app.logger.info('Received new data for list from user_id %s: %s', flask.ext.login.current_user.id, flask.request.form)
    with easypg.cursor() as cur:
        entry_status, messages, list_id = lists.add_book_to_list(cur, flask.ext.login.current_user.id, flask.request.form)
        app.logger.info("Review submitted %s - %s - %s", entry_status, messages, list_id)
        if entry_status:
            for message in messages:
                flask.flash(message)
            return flask.redirect(flask.request.args.get("next") or flask.url_for("display_list", lid=list_id))
        else:
            for message in messages:
                errors.append(message)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("reviews_index")

    return flask.redirect(next)

@app.route("/list/<lid>")
def display_list(lid):
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            list_info = lists.get_list(cur,lid,flask.ext.login.current_user.id)
        else:
            list_info = lists.get_list(cur,lid)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")
    return flask.render_template("list.html",
                                 list=list_info,
                                 next=next)

@app.route("/list")
def lists_index():

    if 'page' in flask.request.args:
        page = int(flask.request.args['page'])
    else:
        page = 1
    if page <= 0:
        flask.abort(404)

    with easypg.cursor() as cur:
        total_pages = lists.get_total_pages(cur)

    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            list_info = lists.get_all_lists(cur, page, flask.session['user_id'])
        else:
            list_info = lists.get_all_lists(cur, page, None)

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1

    return flask.render_template('lists_list.html',
                                 lists=list_info,
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage)

#Reference: http://flask.pocoo.org/docs/0.10/patterns/jquery/
@app.route("/list/_current_user")
@flask.ext.login.login_required
def get_user_lists():
    user_id = flask.ext.login.current_user.id
    with easypg.cursor() as cur:
        user_logs = users.get_user_lists(cur, user_id)
    return flask.jsonify(user_logs)

################## Ratings #############################################################################################

@app.route("/books/rating/add/<bid>", methods=['POST'])
@flask.ext.login.login_required
def add_book_rating(bid):
    rating = flask.request.form['rating']
    book_id = bid
    # print flask.request.form
    user_id = flask.request.form['user_id']
    user = BooknetUser.get(user_id)
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
    if flask.ext.login.current_user.is_authenticated():
        user_id = flask.session['user_id']
    else:
        user_id = None
    

    
    
    with easypg.cursor() as cur:
        message = books.remove_rating(cur, book_id, user_id)

    flask.flash(message)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
        return flask.redirect(next)
    return flask.redirect(flask.url_for('books_index'))


###################### Reviews ###########################

@app.route("/reviews/book/<bid>")
def display_reviews_for_book(bid):
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)

    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            current_user_id = flask.ext.login.current_user.id
        else:
            current_user_id = None
        total_pages, review_info = reviews.get_reviews_by_book(cur, start, limit, bid, current_user_id)

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1

    return flask.render_template('review_list.html',
                                 reviews=review_info['reviews'],
                                 page_title='Reviews for: %s' % review_info['book_info']['title'],
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage)

@app.route("/reviews/<rid>")
def display_review(rid):
    with easypg.cursor() as cur:
        review_info = reviews.get_review(cur,rid)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("reviews_index")
    return flask.render_template("review.html",
                          review=review_info,
                          next=next)

@app.route("/reviews/add/<bid>", methods=['GET', 'POST'])
@flask.ext.login.login_required
def add_review(bid):
    errors = []
    if flask.request.method == 'POST':
        app.logger.info('Received new data for review from user_id %s: %s', flask.ext.login.current_user.id, flask.request.form)
        with easypg.cursor() as cur:
            entry_status, messages, review_id = reviews.add_review(cur, bid, flask.ext.login.current_user.id, flask.request.form)
            app.logger.info("Review submitted %s - %s - %s", entry_status, messages, review_id)
            if entry_status:
                for message in messages:
                    flask.flash(message)
                return flask.redirect(flask.request.args.get("next") or flask.url_for("display_review", rid=review_id))
            else:
                for message in messages:
                    errors.append(message)
    with easypg.cursor() as cur:
        book_info = books.get_book(cur, bid, flask.ext.login.current_user.id)
        # print book_info['user_rating']
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("reviews_index")

    return flask.render_template("review_add_form.html",
                                 book_info=book_info,
                                 error=errors,
                                 next=next)



@app.route("/reviews")
def reviews_index():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)

    with easypg.cursor() as cur:
        total_pages, review_info = reviews.get_review_range(cur, start, limit)

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
                                 page_title='Reviews',
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage)




################### Moderation / Current User Actions ##################################################################

@app.route("/dashboard/")
@flask.ext.login.login_required
def user_dashboard():
    if flask.ext.login.current_user.is_authenticated():
        current_user_id = flask.session['user_id']
    else:
        current_user_id = None
    with easypg.cursor() as cur:
        user_info = users.get_user(cur, current_user_id, current_user_id)

    # print user_info
    return flask.render_template('dashboard_overview.html',
                                 user_info = user_info)
@app.route("/dashboard/logs")
@flask.ext.login.login_required
def user_dashboard_logs():
    user_info = None
    if flask.ext.login.current_user.is_authenticated():
        current_user_id = flask.session['user_id']
    else:
        current_user_id = None
    with easypg.cursor() as cur:
        user_info = users.get_user(cur, current_user_id, current_user_id)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("user_dashboard")
    return flask.render_template('dashboard_logs.html',
                                 user_id=current_user_id,
                                 selected_user=user_info,
                                 next=next)

@app.route("/dashboard/lists")
@flask.ext.login.login_required
def user_dashboard_lists():
    user_info = None
    if flask.ext.login.current_user.is_authenticated():
        current_user_id = flask.session['user_id']
    else:
        current_user_id = None
    with easypg.cursor() as cur:
        user_info = users.get_user(cur, current_user_id, current_user_id)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("user_dashboard")
    return flask.render_template('dashboard_lists.html',
                                 user_id=current_user_id,
                                 selected_user=user_info,
                                 next=next)

@app.route("/dashboard/reviews")
@flask.ext.login.login_required
def user_dashboard_reviews():
    user_info = None
    if flask.ext.login.current_user.is_authenticated():
        current_user_id = flask.session['user_id']
    else:
        current_user_id = None
    with easypg.cursor() as cur:
        user_info = users.get_user(cur, current_user_id, current_user_id)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("user_dashboard")
    return flask.render_template('dashboard_reviews.html',
                                 user_id=current_user_id,
                                 selected_user=user_info,
                                 next=next)

@app.route("/dashboard/followers")
def user_dashboard_followers():
    return flask.render_template('dashboard_followers.html')

@app.route("/dashboard/following")
@flask.ext.login.login_required
def user_dashboard_following():
    with easypg.cursor() as cur:
        user_info = users.get_user_feed(cur,flask.ext.login.current_user.get_id())
    # user_info['name'] = flask.ext.login.current_user.name
    return flask.render_template('dashboard_following.html',
                                 user_info=user_info)

@app.route("/profile")
@flask.ext.login.login_required
def current_user_profile():
    return display_user_profile(flask.ext.login.current_user.id)

@app.route("/dashboard/moderation")
@flask.ext.login.login_required
def moderator_dashboard():

    with easypg.cursor() as cur:
        mod_info = users.get_moderation_info(cur)
    return flask.render_template('dashboard_moderation.html',
                                 mod_info=mod_info)

@app.route("/dashboard/presentation")
@flask.ext.login.login_required
def moderator_presentation():

    return flask.render_template('dashboard_presentation.html')



@app.route("/dashboard/approve/<request_id>")
@flask.ext.login.login_required
def approve_request(request_id):
    raise NotImplementedError
    errors = []
    if flask.request.method == 'POST':
        with easypg.cursor() as cur:
            edit_status, messages, book_id = users.approve_request(cur, request_id, flask.ext.login.current_user.id, flask.request.form)
            print "Posted book data: %s..." % messages
            if edit_status:
                for message in messages:
                    flask.flash(message)
                return flask.redirect(flask.request.args.get("next") or flask.url_for("display_book", bid=book_id))
            else:
                for message in messages:
                    errors.append(message)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("home_index")

    book_info = {'title': 'New Book Addition', 'core_id': '0'}
    return flask.render_template("book_edit_form.html",
                                 book_info=book_info,
                                 page_title="Add A Book!",
                                 error=errors,
                                 next=next)


@app.route("/dashboard/reject/<request_id>")
@flask.ext.login.login_required
def reject_request(request_id):
    raise NotImplementedError
#####################  User Management #################################################################################

@app.route("/user/<uid>")
def display_user_profile(uid):
    # selected_user = BooknetUser.get(uid)
    user_info = None
    if flask.ext.login.current_user.is_authenticated():
        current_user_id = flask.session['user_id']
    else:
        current_user_id = None
    with easypg.cursor() as cur:
        user_info = users.get_user(cur, uid, current_user_id)
    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = flask.url_for("users_index")
    return flask.render_template('user_profile.html',
                                 user_id=uid,
                                 selected_user=user_info,
                                 next=next)

@app.route("/user/follow/<uid>")
@flask.ext.login.login_required
def follow_user(uid):
    followee = BooknetUser.get(uid)
    if flask.ext.login.current_user.is_authenticated():
        follower = flask.session['user_id']
    else:
        follower = None
    with easypg.cursor() as cur:
        message = users.add_follower(cur, followee, follower)

    flask.flash(message)
    if 'next' in flask.request.args:
        return flask.redirect(flask.request.args['next'])

    return flask.redirect(flask.url_for('users_index'))

@app.route("/user/unfollow/<uid>")
def unfollow_user(uid):
    followee = BooknetUser.get(uid)
    if flask.ext.login.current_user.is_authenticated():
        follower = flask.session['user_id']
    else:
        follower = None
    with easypg.cursor() as cur:
        message = users.remove_follower(cur, followee, follower)

    flask.flash(message)
    if flask.request.form['next']:
        return flask.redirect(flask.request.form['next'])

    return flask.redirect(flask.url_for('users_index'))

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
        if flask.ext.login.current_user.is_authenticated():
            user_info = users.get_all_users(cur, page, flask.session['user_id'])
        else:
            user_info = users.get_all_users(cur, page)

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


#################### Login Registration ################################################################################
@app.route("/user/login", methods=['GET', 'POST'])
def login_index():
    # Login page

    errors = []
    if flask.request.method == 'POST':
        # login and validate the user...
        with easypg.cursor() as cur:

            login_status = users.validate_login(cur, flask.request.form)
            if login_status > 0:
                user = BooknetUser.get(login_status)
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

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = None
    return flask.render_template("login.html", errors=errors, next=next)

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
                    user = BooknetUser.get(id)
                    try:
                        if flask.request.form['remeberLogin'] == "remeber-me":
                            remember = True
                    except KeyError:
                        remember = False
                    flask.ext.login.login_user(user, remember)
                    flask.flash("Registered and Logged in successfully.")
                    flask.flash("Good to meet you %s!" % flask.request.form['username'])
                    return flask.redirect(flask.url_for('home_index'))
                else:
                    errors.append(message)

    if 'next' in flask.request.args:
        next = flask.request.args['next']
    else:
        next = None
    return flask.render_template("register.html", errors=errors, next=next)

@app.route("/user/logout")
@flask.ext.login.login_required
def logout():
    flask.ext.login.logout_user()
    flask.flash("You have been logged out!")
    return flask.redirect(flask.url_for('home_index'))


###################################### Search ##########################################################################
@app.route('/search')
def search_index():
    page, sorting, sort_direction = parse_sorting()
    start, limit = get_item_limits(page)



    if 'q' in flask.request.args:
        query = flask.request.args['q']
    else:
        flask.abort(400)
    with easypg.cursor() as cur:
        if flask.ext.login.current_user.is_authenticated():
            total_pages, results = books.search_books(cur, query, start, limit, flask.session['user_id'], sorting, sort_direction)
        else:
            total_pages, results = books.search_books(cur, query, start, limit, None, sorting, sort_direction)

    if page > 1:
        prevPage = page - 1
    else:
        prevPage = None

    if page == total_pages:
        nextPage = None
    else:
        nextPage = page + 1

    sort_options = {}
    return flask.render_template('book_search_results.html',
                                 data=results,
                                 page=page,
                                 totalPages=total_pages,
                                 nextPage=nextPage,
                                 prevPage=prevPage,
                                 sorting=sorting,
                                 sort_direction=sort_direction,
                                 sort_options=sort_options,
                                 parameters='&q=%s' % query,
                                 page_title='Search Results - %s' % query,
                                 search=query)
    # return render_books_index('book_search_results.html', results, total_pages, sort_options, '')



####################################### Utility ########################################################################
def get_item_limits(page):
    return ((page - 1) * ITEMS_PER_PAGE), ITEMS_PER_PAGE







if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

