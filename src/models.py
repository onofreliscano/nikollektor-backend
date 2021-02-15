import os 
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class HumanTalent (db.Model):
    '''clase para Human Talent'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(80), unique=False, nullable=False)
    full_name = db.Column(db.String(120), unique=False, nullable=False)
    salt=db.Column(db.String(120),nullable=False)
    moods=db.relationship("Mood", backref="human_talent")
    team_id=db.Column(db.Integer,db.ForeignKey("team.id"))

    def __init__(self, data):
        self.email = data['email']
        self.salt = b64encode(os.urandom(4)).decode("utf-8")
        self.hashed_password = self.set_password(data["hashed_password"])
        self.full_name = data['full_name']
    
    @classmethod
    def create_ht(cls, data):
        human_talent=cls(data)
        db.session.add(human_talent)
        db.session.commit()
        return human_talent

    def set_password(self,password):
        self.hashed_password = generate_password_hash(f"{password}{self.salt}")
    
    def check_password(self,password):
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name":self.full_name,
            # "moods":self.moods,
            "hashed_password":self.hashed_password
            # "team_name":self.team_name
        }
       
class HRManager(db.Model):
    '''clase para manager'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    hashed_password = db.Column(db.String(80), unique=True, nullable=False)
    salt=db.Column(db.String(120),unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))

    def __init__(self, email, full_name, password):
        self.email=email,
        self.full_name=full_name,
        self.hashed_password=self.set_password(password)
        self.salt=b64encode(os.urandom(4)).decode("utf-8"),

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name":self.full_name
        }

    @classmethod
    def create(cls, email, full_name, password):
        _full_name = full_name.lower()
        h_r_manager=cls(
            email,
            _full_name,
            password
        )
        db.session.add(h_r_manager)
        db.session.commit()
        return h_r_manager
    
    def set_password(self,password):
        self.hashed_password = generate_password_hash(f"{password}{self.salt}")
        # return generate_password_hash(
        #     f"{password}{self.salt}",
        #     self.salt
        # )
    
    def check_password(self,password):
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )

class Company(db.Model):
    '''clase para Company'''
    id= db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),unique=False)
    image=db.Column(db.String(120), nullable=True)
    country=db.Column(db.String(120),unique=False)
    city=db.Column(db.String(120),unique=False)
    identifier=db.Column(db.String(120),unique=False)
    teams=db.relationship("Team", backref="company")
    managers=db.relationship("HRManager", backref="company")

    def __init__(self, name, image, country, city, identifier):
        self.name=name,
        self.image=image,
        self.country=country,
        self.city=city,
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

    @classmethod
    def create_c(cls, name, image, country, city, identifier):
        company=cls(
            name,
            image,
            country.lower(),
            city.lower(),
            identifier
        )
        db.session.add(company)
        db.session.commit()
        return company
    
class Team(db.Model):
    '''clase para Team'''
    id= db.Column(db.Integer,primary_key= True)
    name=db.Column(db.String(120),unique=False)
    description=db.Column(db.String(200),unique=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    members=db.relationship("HumanTalent", backref="team")

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "description":self.description
        }

class Mood(db.Model):
    '''clase para mood'''
    id = db.Column(db.Integer, primary_key=True)
    date_published = db.Column(db.Integer)
    face_value = db.Column(db.Integer)
    comment = db.Column(db.String(120), unique=False, nullable=False)
    human_talent_id=db.Column(db.Integer,db.ForeignKey("human_talent.id"))

    def serialize(self):
        return{
            "id" : self.id,
            "date_published" : self.date_published,
            "face_value" : self.face_value,
            "comment" : self.comment,
        }
