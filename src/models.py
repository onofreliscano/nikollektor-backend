import os 
import datetime
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class HumanTalent (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    salt=db.Column(db.String(120),nullable=False)
    hashed_password = db.Column(db.String(120), unique=False, nullable=False)
    full_name = db.Column(db.String(120), unique=False, nullable=False)
    img_url = db.Column(db.String(120))
    moods=db.relationship("Mood", backref="human_talent")
    team_id=db.Column(db.Integer,db.ForeignKey("team.id"))

    def set_password(self,password):
        self.hashed_password = generate_password_hash(f"{password}{self.salt}")
    
    def check_password(self,password):
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )

    def __init__(self, email, password, full_name, team_id, img_url):
        self.email = email
        self.salt = b64encode(os.urandom(4)).decode("utf-8")
        self.set_password(password)
        self.full_name = full_name
        self.img_url = img_url
        self.team_id= team_id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "img_url": self.img_url,
            "team_id": self.team_id
        }
       
class HRManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    salt=db.Column(db.String(120),unique=True)
    hashed_password = db.Column(db.String(120), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    
    def set_password(self,password):
        self.hashed_password = generate_password_hash(f"{password}{self.salt}")
    
    def check_password(self,password):
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )

    def __init__(self, email, full_name, password, company_id):
        self.email=email
        self.full_name=full_name
        self.salt=b64encode(os.urandom(4)).decode("utf-8")
        self.set_password(password)
        self.company_id=company_id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name":self.full_name,
            "company_id":self.company_id
        }

class Company(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),unique=False)
    image=db.Column(db.String(120), nullable=True)
    country=db.Column(db.String(120),unique=False)
    city=db.Column(db.String(120),unique=False)
    identifier=db.Column(db.String(120),unique=True)
    teams=db.relationship("Team", backref="company")
    managers=db.relationship("HRManager", backref="company")

    def __init__(self, name, image, country, city, identifier):
        self.name=name
        self.image=image
        self.country=country
        self.city=city
        self.identifier=identifier
    
    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "image":self.image,
            "city":self.city,
            "country":self.country,
            "identifier":self.identifier
        }

class Team(db.Model):
    id= db.Column(db.Integer,primary_key= True)
    name=db.Column(db.String(120),unique=False)
    description=db.Column(db.String(200),unique=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    members=db.relationship("HumanTalent", backref="team")

    def __init__(self,name,description,company_id):
        self.name=name
        self.description=description
        self.company_id=company_id

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "description":self.description,
            "company_id":self.company_id
        }

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_published = db.Column(db.DateTime(timezone=True), nullable=False)
    face_value = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), unique=False, nullable=True)
    human_talent_id=db.Column(db.Integer,db.ForeignKey("human_talent.id"))

    def __init__(self, face_value, comment, human_talent_id):
        self.date_published = datetime.datetime.now(datetime.timezone.utc)
        self.face_value = face_value
        self.comment = comment
        self.human_talent_id = human_talent_id
    
    def get_date(self):
        return self.date_published.strftime("%x")         
        
    def serialize(self):
        return{
            "id" : self.id,
            "date_published" : self.get_date(),
            "face_value" : self.face_value,
            "comment" : self.comment,
            "human_talent_id": self.human_talent_id
        }
