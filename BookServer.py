import flask
from lib import easypg1
from lib import books, users

easypg.config_name = 'bookserver'

app = flask.Flask('BookServer')
def get_resource_as_string(name, charset='utf-8'):
    # http://flask.pocoo.org/snippets/77/
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

# during developement
app.debug = True

@app.route("/")
def home():
    #with easypg.cursor() as cur:
    #    narts = articles.get_article_count(cur)
    #    nproc, nser = proceedings.get_proceedings_stats(cur)
    #    stats = {'narticles': narts, 'nproceedings': nproc, 'nseries': nser}
    return flask.render_template('home.html')

@app.route("/user/<uid>")
def display_user(uid):
    # Other user's profile page
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
    app.run()
