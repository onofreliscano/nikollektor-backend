"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, HRManager, HumanTalent, Mood, Company, Team
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
#from models import Person
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JWT_SECRET_KEY'] = 'mariposas'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
# generate sitemap with all your endpoints

@app.route('/')
def sitemap():
    return generate_sitemap(app)


# AL 16 de FEB
# MODIFICACION PARA CLASE COMPANY
# INCLUSION DE ENDPOINTS:

@app.route('/signup_company', methods=['POST'])
def handle_signup_company():
    
    data = request.get_json()

    if data is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'name' not in data:
        raise APIException("You need to specify the company's name", status_code=400)
    if 'city' not in data:
        raise APIException('You need to specify the city', status_code=400)
    if 'country' not in data:
        raise APIException('You need to specify the country', status_code=400)
    if 'identifier' not in data:
        raise APIException('You need to specify the phone', status_code=400)
    
    new_company = Company.create_c(name=data['name'], image=data['image'], country=data['country'], city=['city'], identifier=data['identifier'])
    if new_company:
        return new_company.serialize(),201

@app.route('/company', methods=['GET'])
@jwt_required
def handle_all_company():
   
    user_email = get_jwt_identity()
    hr_manager = HRManager.query.filter_by(email=user_email).one_or_none()

    if hr_manager is None:
        return 403
        
    return jsonify(hr_manager.company.serialize()), 200

# FIN DE ENDPOINTS CLASE COMPANY




@app.route('/signup_manager', methods=['POST'])
def handle_signup_manager():

    data = request.get_json()

    if data is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'email' not in data:
        raise APIException('You need to specify the email', status_code=400)
    if 'full_name' not in data:
        raise APIException('You need to specify the full_name', status_code=400)
    if "password" not in data:
        raise APIException('You need to specify the password', status_code=400)

    new_hrmanager = HRManager(email=data['email'], full_name=data['full_name'], password=data["password"], company_id=data['company_id'])
    db.session.add(new_hrmanager)
    db.session.commit()
    if new_hrmanager:
        return new_hrmanager.serialize(),201

# def handle_signup_manager():
#     data = request.json   
#     new_hrmanager = HRManager.create(email=data['email'], full_name=data['full_name'], password=data['password'])
#     if new_hrmanager:
#         return new_hrmanager.serialize(),201

@app.route("/login", methods=["POST"])
def handle_login():
    """ 
        check password for user with email = body['email']
        and return token if match.
    """
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    email = data.get('email', None)
    password = data.get('password', None)

    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    user = HumanTalent.query.filter_by(email=email).one_or_none()
    admin = HRManager.query.filter_by(email=email).one_or_none()
    
    if not user or admin:
        return jsonify({"msg": "User does not exist"}), 404
    if user.check_password(password):
        response = {'jwt': create_access_token(identity=user.email), 'is_manager':False} #aquí crea el token del login
        return jsonify(response), 200
    if admin.check_password(password):
        response = {'jwt': create_access_token(identity=admin.email), 'is_manager':True} #aquí crea el token del login
        return jsonify(response), 200
    else:
        return jsonify({"msg": "Bad credentials"}), 401

@app.route('/HRManager/teams')
def handle_all_team():
    """Devuelve la lista de Team"""
    teams = Team.query.all()
    response_body = []
    for team in teams:
        response_body.append(team.serialize())
    return jsonify(response_body), 200

#este endpoint funciona

@app.route('/HRManager/team_create', methods=['POST'])
def handle_create():
    data = request.json
    new_team = Team.create(data)
    if new_team :
        return new_team.serialize(),201

@app.route('/HRManager/new_talent', methods=['POST'])
def handle_new_talent():
    """Registra un HumanTalent"""
    data = request.get_json()
    new_talent = HumanTalent.create_ht(data)
    if new_talent :
        #return new_hrmanager.serialize(),201
        return new_talent.serialize(),201

@app.route('/HRManager/human_talent')
def handle_all_human_talent():
    """Devuelve la lista de talento humano"""
    humans_talent = HumanTalent.query.all()
    response_body = []
    for human in humans_talent:
        response_body.append(human.serialize())
    return jsonify(response_body), 200

#este endpoint funciona

@app.route("/HRManager/human_talent/<int:id>")
def handle_human_talent(id):
    """ buscar y regresar un talento humano"""
    human_talent = HumanTalent.query.get(id)
    if isinstance(human_talent, HumanTalent):
        return jsonify(human_talent.serialize()), 200
    else:
        return jsonify({
            "result": "user not found"
        }), 404

#este endpoint funciona

@app.route("/identity")
@jwt_required
def handle_seguro():
    email = get_jwt_identity() #nos va dar la identidad de token
    return jsonify({"msg":f"Hola, {email}"})

@app.route("/HumanTalent", methods=["POST"]) #hacer GET
def handle_mood():
    """ Envía el mood del día """
    data = request.get_json()
    if data is None:
        return jsonify({
            "result" : "missing request body"
        }), 400
    if not face_value:
        return jsonify({"msg": "Missing your mood parameter"}), 400
    if not date_published:
        return jsonify({"msg": "Missing date parameter"}), 400 
    
    new_mood = Mood(face_value=data['face_value'], date=data[date_published], comment=data['comment']) #pasamos los parametros
    db.session.add(new_mood) # añade un mood en la base de datos, lo deja en cola
    try:
       db.session.commit() # intentas que se integre el cambio
       return jsonify(new_mood.serialize()), 201
    except Exception as error:
        print(error.args) 
        return jsonify("NOT OK"), 500

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)