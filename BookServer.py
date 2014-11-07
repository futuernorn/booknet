import flask
import easypg


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


if __name__ == "__main__":
    app.run()
