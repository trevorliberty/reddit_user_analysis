from flask import Flask
from flask import render_template
from flask_fontawesome import FontAwesome
from .models import User

app = Flask(__name__)
app.secret_key = 'secret_key'
fa = FontAwesome(app)

app.add_url_rule('/api/<redditusername>',
                 view_func=User.as_view('user'),
                 methods=['GET', 'POST'])


@app.route('/')
def index():
    """
    Landing Page
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
