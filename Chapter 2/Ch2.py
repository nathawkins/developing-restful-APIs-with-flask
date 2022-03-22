from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return("Hello World!")

@app.route('/super_simple')
def super_simple():
    return(jsonify(message = "Hello from the Planetary API! Boo Yah!"))

@app.route('/not_found')
def not_found():
    return(jsonify(message = "That resource was not found"), 404)
    
@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age  = int(request.args.get('age'))
    print(name, age)
    if age < 18:
        msg  = jsonify(message = "Sorry," + name + ", but you are not old enough.")
        code = 401
    else:
        msg  = jsonify(message = "Welcome, " + name + "!")
        code = 200
    return(msg, code)
    
@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        msg  = jsonify(message = "Sorry," + name + ", but you are not old enough.")
        code = 401
    else:
        msg  = jsonify(message = "Welcome, " + name + "!")
        code = 200
    return(msg, code)

if __name__ == '__main__':
    app.run()