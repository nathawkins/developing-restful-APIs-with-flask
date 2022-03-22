from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
import os

app     = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret' # change this for deployment
#app.config['MAIL_SERVER']   = os.environ['MAIL_SERVER']
#app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
#app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)

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
    
@app.route('/register', methods = ['POST'])
def register():
    email = request.form['email']
    test  = User.query.filter_by(email = email).first()
    if test:
        return(jsonify(message = "User exists with email address. Please try again."), 409)
    first_name = request.form['first_name']
    last_name  = request.form['last_name']
    password   = request.form['password'] 
    user = User(first_name = first_name, last_name = last_name, email = email, password = password)
    db.session.add(user)
    db.session.commit()
    return(jsonify(message = "User created successfully!"), 201)
    
@app.route('/login', methods = ['POST']) # controversial
def login():
    if request.is_json:
        email    = request.json['email']
        password = request.json['password']
    else:
        email    = request.form['email']
        password = request.form['password']
       
    test = User.query.filter_by(email = email, password = password).first()
    if test:
        access_token = create_access_token(identity=email)
        return(jsonify(message = "Login Successful", access_token = access_token))
    else:
        return(jsonify(message = "Wrong email or password"),401)
    
@app.route('/retrieve_password/<string:email>', methods = ['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email = email).first()
    if user:
        # Body of email to send 
        msg = Message("Your planetary API password is " + user.password,
                       sender = "admin@planetary-api.com",
                       recipients = [email])
        mail.send(msg)
        return(jsonify(message = "Email with password has been sent to " + email))
    return(jsonify(message = "Email does not exist"), 401)
    
@app.route('/planet_details/<int:planet_id>', methods = ['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id = planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return(jsonify(result))
    else:
        return(jsonify(message = "No data entry for planet"), 404)
    
@app.route('/add_planet', methods = ['POST'])
@jwt_required()
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name = planet_name).first()
    if test:
        return(jsonify(message = "Planet entry already exists in database"), 409)
    planet_type = request.form['planet_type']
    home_star = request.form['home_star']
    mass = float(request.form['mass'])
    radius = float(request.form['radius'])
    distance = float(request.form['distance'])
    new_planet = Planet(planet_name = planet_name,
                        planet_type = planet_type,
                        home_star = home_star,
                        radius = radius,
                        mass = mass,
                        distance = distance)
    db.session.add(new_planet)
    db.session.commit()
    return(jsonify(message = "Planet addedd successfully!"), 201)
    
@app.route('/update_planet', methods = ['PUT'])
@jwt_required()
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id = planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star   = request.form['home_star']
        planet.mass        = float(request.form['mass'])
        planet.radius      = float(request.form['radius'])
        planet.distance    = float(request.form['distance'])
        # No need for db call for updating
        db.session.commit()
        return(jsonify(message = "Planet updated successfully!"), 202)
    return(jsonify(message = "No planet entry for planet with id " + str(planet_id)), 404)
    
@app.route('/delete_planet/<int:planet_id>', methods = ['DELETE'])
@jwt_required()
def delete_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id = planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return(jsonify(message = "Successfully deleted planet..."), 202)
    return(jsonify(message = "No planet found with corresponding planet id"), 404)
    
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