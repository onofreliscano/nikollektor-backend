"""
fsdfsdsdf
JOSEFA UPDATES
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, HumanTalent, HRManager, Team, Company
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
'''
@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route("/signup", methods=["POST"])
def handle_signup():
    """ creates an user and returns it. """
    data = request.json
    new_user = User.create(data)
    if new_user:
        return new_user.serialize(), 201

'''
# ENDPOINTS creados por Josefa y Onofre

@app.route('/signup', methods=['POST'])
def handle_signup():
    data = request.json
    new_hrmanager = HRManager.create(data)
    new_company = Company.create(data)
    new_client = f"{new_hrmanager} {new_company}"
    if new_client :
        #return new_hrmanager.serialize(),201
        return new_client.serialize(),201

@app.route('/Team/create', methods=['POST'])
def handle_create():
    data = request.json
    new_team = Team.create(data)
    if new_team :
        #return new_hrmanager.serialize(),201
        return new_team.serialize(),201

@app.route('/HRManager/IncludeTalent', methods=['POST'])
def handle_IncludeTalent():
    data = request.json
    new_talent = HumanTalent.create(data)
    if new_talent :
        #return new_hrmanager.serialize(),201
        return new_talent.serialize(),201





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
