import os
from flask import Flask, request, jsonify, url_for
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


# para poder ingresar a la app se debe registrar primero la compañía 
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

# seguidamente, se debe registrar el HR Manager, quien requiere el id de la compañía
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


# inicio de sesión para ambos tipos de usuarios
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


# el HR Manager puede hacer GET de la tabla Company.
@app.route('/company', methods=['GET'])
@jwt_required
def handle_all_company():
    """ verifica que el token pertenezca a un usuario de la tabla HR Manager para poder autorizar el GET """
   
    user_email = get_jwt_identity()
    hr_manager = HRManager.query.filter_by(email=user_email).one_or_none()

    if hr_manager is None:
        return 403
        
    return jsonify(hr_manager.company.serialize()), 200


# endpoints para tabla Team
@app.route('/teams')
def handle_all_team():
    """Devuelve la lista de Team"""
    teams = Team.query.all()
    response_body = []
    for team in teams:
        response_body.append(team.serialize())
    return jsonify(response_body), 200

@app.route('/team/<int:id>', methods=['DELETE'])
def delete_team(id): 
    """ elimina un team por su ID"""
    db.session.delete(Team.query.get(id) )
    db.session.commit() 
    return '', 204

@app.route('/team_create', methods=['POST'])
@jwt_required
def handle_create():
    """Crea Team, necesario para poder crear un usuario human talent"""

    hrmanager_email = get_jwt_identity()
    human_t = HRManager.query.filter_by(email=hrmanager_email).one_or_none()

    data = request.get_json()

    if data is None:
            return jsonify({
                "result" : "missing request body"
            }), 400
    if "name" not in data:
            return jsonify({"msg": "Missing name parameter"}), 400
    if "description" not in data:
            return jsonify({"msg": "Missing date parameter"}), 400 
    if "company_id" not in data:
            return jsonify({"msg": "Missing company.id parameter"}), 400
    
    new_team = Team(name=data["name"],description=data["description"],company_id=data["company_id"])
    db.session.add(new_team)
    db.session.commit()
    if new_team :
        return new_team.serialize(),201


# endpoints para consultar y crear un usuario de la tabla HumanTalent
@app.route('/human_talent', methods=['POST'])
def handle_new_talent():
    """Registra un HumanTalent"""

    data = request.get_json()

    new_talent = HumanTalent(email=data["email"], password=data["password"], full_name=data["full_name"], team_id=data["team_id"],img_url=data["img_url"])
    db.session.add(new_talent)
    db.session.commit()
    if new_talent:
        return new_talent.serialize(),201

@app.route('/human_talent')
def handle_all_human_talent():
    """Devuelve la lista de talento humano"""
    humans_talent = HumanTalent.query.all()
    response_body = []
    for human in humans_talent:
        response_body.append(human.serialize())
    return jsonify(response_body), 200

@app.route("/human_talent/<int:id>")
def handle_human_talent_single(id):
    """ buscar y regresar un talento humano"""
    human_talent = HumanTalent.query.get(id)
    if isinstance(human_talent, HumanTalent):
        return jsonify(human_talent.serialize()), 200
    else:
        return jsonify({
            "result": "user not found"
        }), 404

@app.route('/human_talent/<int:id>', methods=['DELETE'])
def delete_human_talent(id): 
    """ elimina un talento humano por su ID"""
    hrmanager_email = get_jwt_identity()
    human_t = HRManager.query.filter_by(email=hrmanager_email).one_or_none()

    db.session.delete(HumanTalent.query.get(id) )
    db.session.commit() 
    return '', 204

# endpoints para usar en las vistas tras el inicio de sesión de un human talent,
# busca al usuario de la tabla HumanTalent por su token, si existe, solo devuelve a ese usuario.
@app.route("/HumanTalent", methods=["GET", "PATCH"])
@jwt_required
def handle_human_talent():
    """Recibe human talent, modifica password"""

    talent_email = get_jwt_identity() #pide al token la identidad del usuario
    
    if request.method == "GET":
        # busca y verifica que el token del login sea el mismo a un HumanTalent o sea ninguno en caso de no hallarlo
        h_talent = HumanTalent.query.filter_by(email=talent_email).one_or_none()

        if h_talent is None:
           return 403
        
        return jsonify(h_talent.serialize()), 200

    if request.method == "PATCH":

        data = request.get_json()
        # hace lo mismo de la línea 201, si coincide el token de login con el guardado en la tabla HumanTalent,
        # autoriza el cambio de contraseña
        human_t = HumanTalent.query.filter_by(email=talent_email).one_or_none()

        if human_t is None:
            raise APIException('Human Talent not found', status_code=404)
        if "password" in data:
            human_t.password = data["password"]
        db.session.commit()
        return jsonify(human_t.serialize()), 200


# endpoints para consultar la tabla Moods, requiere un token para autorizar ambos métodos,
# el usuario debe pertenecer a la tabla HumanTalent.
@app.route("/moods", methods=["POST", "GET"])
@jwt_required
def handle_human_mood():

    talent_email = get_jwt_identity()
    human_t = HumanTalent.query.filter_by(email=talent_email).one_or_none()


    if request.method == "GET":

        moods=Mood.query.filter_by(human_talent_id=human_t.id).all()
        mood_list=[]
        for mood in moods:
            mood_list.append(mood.serialize())
        return jsonify(mood_list), 200
    
    if request.method == "POST":

        data = request.get_json()

        if data is None:
            return jsonify({
                "result" : "missing request body"
            }), 400
        if "face_value" not in data:
            return jsonify({"msg": "Missing your mood parameter"}), 400
    
        new_mood = Mood(face_value=data['face_value'], comment=data['comment'],human_talent_id=human_t.id) 
        db.session.add(new_mood) 
        try:
            db.session.commit()
            return jsonify(new_mood.serialize()), 201
        except Exception as error:
            print(error.args) 
            return jsonify("NOT OK"), 500


# endpoint para devolver la tabla Mood sin autorización. Para usar mood.face_value en la generación de las gráficas.
@app.route('/mood')
def handle_all_moods():
    """Devuelve la lista de moods"""
    all_moods = Mood.query.all()
    response_body = []
    for mood in all_moods:
        response_body.append(mood.serialize())
    return jsonify(response_body), 200


# no ha sido utilizado
# @app.route("/identity")
# @jwt_required
# def handle_seguro():
#     email = get_jwt_identity()
#     return jsonify({"msg":f"Hola, {email}"})



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)