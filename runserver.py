from os import environ

from flask import Flask
app = Flask(__name__)
# from application import app

@app.route('/')
@app.route('/home')
def home():
    return 'This is an app'

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555    
    app.run(debug=True)
    app.run(HOST, PORT)
