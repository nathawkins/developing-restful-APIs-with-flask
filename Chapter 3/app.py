from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
import os

app     = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')

db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created!')
    
@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Destroyed!')
    
@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name = 'Mercury', 
                     planet_type = 'Class D',
                     home_star = 'Sol',
                     mass = 3.28e23,
                     radius = 1516,
                     distance = 35.98e6)
    
    venus = Planet(planet_name = 'Venus', 
                   planet_type = 'Class K',
                   home_star = 'Sol',
                   mass = 4.867e24,
                   radius = 3760,
                   distance = 67.24e6)
                     
    earth = Planet(planet_name = 'Earth', 
                   planet_type = 'Class M',
                   home_star = 'Sol',
                   mass = 5.972e24,
                   radius = 3959,
                   distance = 92.96e6)
                   
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)
    
    test_user = User(first_name = "William",
                     last_name = "Shatner",
                     email = "tng@startrek.com",
                     password = "P@ssw0rd")
                     
    db.session.add(test_user)
    db.session.commit()
    
    print('Database Seeded!')
    
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
    
@app.route('/planets', methods = ['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return(jsonify(result))

    
## Database models (could split into separate files and load as library)
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique = True) ## Constrain to unique value in field for db
    password = Column(String)
    
class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key = True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)
    
class UserSchema(ma.Schema):
    class Meta:
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        
class PlanetSchema(ma.Schema):
    class Meta:
        fields = ['planet_id', 'planet_name', 'planet_type', 'home_star', 'mass', 'radius', 'distance']
        
user_schema  = UserSchema()
users_schema = UserSchema(many = True)
planet_schema  = PlanetSchema()
planets_schema = PlanetSchema(many = True)
    

if __name__ == '__main__':
    app.run()