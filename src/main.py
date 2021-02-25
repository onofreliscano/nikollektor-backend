import os
from flask import Flask, request, jsonify, url_for, redirect
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, HRManager, HumanTalent, Mood, Company, Team
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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

"""
ENPOINTS: Company
"""

@app.route('/signup_company', methods=['POST'])
def handle_signup_company():
    """ Registra una compañía, desde la que se podrá crear al HR manager"""
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
    new_company = Company(name=data['name'], image=data['image'], country=data['country'], city=data['city'], identifier=data['identifier'])
    db.session.add(new_company)
    db.session.commit()
    if new_company:
        return new_company.serialize(),201

@app.route('/company', methods=['GET'])
@jwt_required()
def handle_all_company():
    user_email = get_jwt_identity()
    hr_manager = HRManager.query.filter_by(email=user_email).one_or_none()
    if hr_manager is None:
        return 403
        return jsonify(hr_manager.company_id.serialize()), 200

@app.route('/company/new_company', methods=['POST'])
def handle_new_company():
    data = request.get_json()
    if data is None:
        raise APIException("onofre's msg: specify the request body as a json object", status_code=400)
    if 'name' not in data:
        raise APIException("onofre's msg: specify an email", status_code=400)
    if 'image' not in data:
        raise APIException("onofre's msg: upload an image", status_code=400)
    if 'country' not in data:
        raise APIException("onofre's msg: specify a country", status_code=400)
    if 'city' not in data:
        raise APIException("onofre's msg: specify a city", status_code=400)
    if 'identifier' not in data:
        raise APIException("onofre's msg: specify an identifier (RIF, CODE)", status_code=400)
    new_company = Company(name=data['name'], image=['image'], country=['country'], city=['city'], identifier=['identifier'])
    db.session.add(new_company)
    db.session.commit()
    if new_company:
        return new_company.serialize(),201

@app.route('/company/update/<int:id>', methods=['PATCH']) #PUT
def handle_company_update(id):
    data = request.get_json()
    update = Company.query.get(id)
    update.name = data['name']
    update.image = data['image']
    update.country = data['country']
    update.city = data['city']
    update.identifier = data['identifier']
    db.session.commit()
    return '', 204

"""
ENPOINTS: HRManager
"""

@app.route('/signup_manager', methods=['POST'])
def handle_signup_manager():
    """registra un HR manager"""
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


@app.route('/HRManager/update/<int:id>', methods=['PATCH']) #PUT
def handle_hrmanager_update(id):
    data = request.get_json()
    update = HRManager.query.get(id)
    update.email = data['email']
    update.full_name = data['full_name']
    update.company_id = data['company_id']
    
    db.session.commit()
    return '', 204



"""
ENPOINTS: LOGIN
"""      

@app.route("/login", methods=["POST"])
def handle_login():
    """ verifica el password de human talent o HR manager con email = data['email'] y genera un token si lo consigue"""
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
    if user:
        if user.check_password(password):
            response = {'jwt': create_access_token(identity=user.email), 'is_manager':False} #aquí crea el token del login
            return jsonify(response), 200
    if admin:
        if admin.check_password(password):
            response = {'jwt': create_access_token(identity=admin.email), 'is_manager':True} #aquí crea el token del login
            return jsonify(response), 200
    if not user or admin:
        return jsonify({"msg": "User does not exist"}), 404
    else:
        return jsonify({"msg": "Bad credentials"}), 401


"""
ENPOINTS: Team
"""


@app.route('/HRManager/teams')
def handle_all_team():
    """Devuelve la lista de Team"""
    teams = Team.query.all()
    response_body = []
    for team in teams:
        response_body.append(team.serialize())
    return jsonify(response_body), 200

@app.route('/HRManager/team/<int:id>', methods=['DELETE'])
def delete_team(id): 
    """ elimina un team por su ID"""
    db.session.delete(Team.query.get(id) )
    db.session.commit() 
    return '', 204

@app.route('/HRManager/team_create', methods=['POST'])
def handle_create():
    """Crea Team, necesario para crear el human talent"""
    data = request.get_json()
    new_team = Team(name=data["name"],description=data["description"],company_id=data["company_id"])
    db.session.add(new_team)
    db.session.commit()
    if new_team :
        return new_team.serialize(),201

@app.route('/HRManager/team/update/<int:id>', methods=['PATCH']) #PUT
def handle_team_update(id):
    data = request.get_json()
    update = Team.query.get(id)
    update.name = data['name']
    update.description = data['description']
    update.company_id = data['company_id']
    
    db.session.commit()
    return '', 204


"""
ENPOINTS: HumanTalent
"""


@app.route('/HRManager/new_talent', methods=['POST'])
def handle_new_talent():
    """Registra un HumanTalent"""
    data = request.get_json()
    new_talent = HumanTalent(email=data["email"], password=data["password"], full_name=data["full_name"], team_id=data["team_id"])
    db.session.add(new_talent)
    db.session.commit()
    if new_talent:
        return new_talent.serialize(),201

@app.route('/HRManager/human_talent')
def handle_all_human_talent():
    """Devuelve la lista de talento humano"""
    humans_talent = HumanTalent.query.all()
    response_body = []
    for human in humans_talent:
        response_body.append(human.serialize())
    return jsonify(response_body), 200

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

@app.route('/HRManager/human_talent/<int:id>', methods=['DELETE'])
def delete_human_talent(id): 
    """ elimina un talento humano por su ID"""
    db.session.delete(HumanTalent.query.get(id) )
    db.session.commit() 
    return '', 204

# @app.route("/identity")
# @jwt_required
# def handle_seguro():
#     email = get_jwt_identity() #nos va dar la identidad de token
#     return jsonify({"msg":f"Hola, {email}"})

@app.route("/HumanTalent", methods=["POST"]) #hacer GET y arreglar
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

@app.route('/HRManager/team/update/<int:id>', methods=['PATCH']) #PUT
def handle_team_update(id):
    data = request.get_json()
    update = Team.query.get(id)
    update.name = data['name']
    update.description = data['description']
    update.company_id = data['company_id']
    db.session.commit()
    return '', 204





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)