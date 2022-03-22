from flask import Flask


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/super_simple')
def hello_simple():
    return("Hello from Planetary API! BOO YAH")

if __name__ == '__main__':
    app.run()
