from flask import Flask
import easypg

app = Flask(__name__)
easypg.config_name = 'bookserver'

@app.route("/")
def main_index(:)
    return "Hello World!"

if __name__ == "__main__":
    app.run()
