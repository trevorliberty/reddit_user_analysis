from flask import Flask
from flask import render_template
from flask_fontawesome import FontAwesome
from src.controllers.renderUser import userView as User

app = Flask(__name__)
app.secret_key = 'secret_key'
fa = FontAwesome(app)

app.add_url_rule('/<username>',
                 view_func=User.as_view('user'),
                 methods=['GET', 'POST'])


@app.route('/')
def index():
    """
    Landing Page
    """
    return render_template('index.html')


@app.errorhandler(404)
def notfound(e):
    """Error Handler for 404 requests if a page is not found"""
    return render_template('404.html'), 404


@app.route('/user/<username>')
def getUser(username):
    return render_template('user.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
