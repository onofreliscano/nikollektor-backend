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

@app.route('/HRManager/human_talent')
def handle_all_human_talent():
    """Devuelve la lista de talento humano"""
    humans_talent = HumanTalent.query.all()
    response_body = []
    for human in humans_talent:
        response_body.append(human.serialize())
    return jsonify(response_body), 200

@app.route("/HRManager/human_talent/<human_talent_id>")
def handle_human_talent():
    """ buscar y regresar un talento humano"""
    human_talent = HumanTalent.query.get(human_talent_id)
    if isinstance(human_talent, HumanTalent):
        return jsonify(human_talent.serialize()), 200
    else:
        return jsonify({
            "result": "user not found"
        }), 404

@app.route("/HRManager/signup", methods=["POST"])
def handle_signup():
    """ creates an user and returns it. """
    data = request.json
    new_user = HumanTalent.create(data)
    if new_user:
        return new_user.serialize(), 201

@app.route("/login", methods=["POST"])
def handle_login():
    """ 
        check password for user with email = body['email']
        and return token if match.
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user = HumanTalent.query.filter_by(email=email).one_or_none()
    if not user:
        return jsonify({"msg": "User does not exist"}), 404
    if user.check_password(password):
        response = {'jwt': create_access_token(identity=user.email)} #aquí crea el token del login
        return jsonify(response), 200
    else:
        return jsonify({"msg": "Bad credentials"}), 401
    # if username != 'test' or password != 'test':
    #     return jsonify({"msg": "Bad username or password"}), 401, 403
    # Identity can be any data that is json serializable

@app.route("/seguro")
@jwt_required
def handle_seguro():
    email = get_jwt_identity() #nos va dar la identidad de token
    return jsonify({"msg":f"Hola, {email}"})

@app.route("/human_talent/profile", methods=['POST'])
def handle_mood():
    """ Envía el mood del día """
    if not face_value:
        return jsonify({"msg": "Missing your mood parameter"}), 400
    if not date_published:
        return jsonify({"msg": "Missing date parameter"}), 400 
   

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)