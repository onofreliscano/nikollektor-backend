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

    # Moods=db.relationship("Mood", backref="HumanTalent")
    moods=db.relationship("Mood", backref="human_talent")
    # Team_id=db.Column(db.Integer,db.ForeignKey("Team.id"))
    team_id=db.Column(db.Integer,db.ForeignKey("team.id"))

    def __init__(self,data):
        self.email=data["email"],
        self.salt=b64encode(os.urandom(4)).decode("utf-8"),
        self.hashed_password=self.set.password(
            data["password"]
        )

    @classmethod
    def create(cls,data):
        human_talent=cls(data)
        db.session.add(human_talent)
        db.session.commit()
        return human_talent
    
    def set_password(self,password):
        return generate_password_hash(
            f"{password}{self.salt}",
            self.salt
        )
    
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
            "hashed_password":self.hashed_password
            }
       
class HRManager(db.Model):
    '''clase para manager'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), unique=False, nullable=False)
    salt=db.Column(db.String(120),unique=False,nullable=False)
    hashed_password = db.Column(db.String(80), unique=False, nullable=False)
    # Company_id = db.Column(db.Integer, db.ForeignKey("Company.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))

    @classmethod
    def create(cls,data):
        h_r_manager=cls(data)
        db.session.add(h_r_manager)
        db.session.commit()
        return h_r_manager
    
    def set_password(self,password):
        return generate_password_hash(
            f"{password}{self.salt}",
            self.salt
        )
    
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
            "hashed_password":self.hashed_password
            }

class Company(db.Model):
    '''clase para Company'''
    id= db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),unique=False)
    image=db.Column(db.String(120),unique=False)
    country=db.Column(db.String(120),unique=False)
    city=db.Column(db.String(120),unique=False)
    identifier=db.Column(db.String(120),unique=False)
   
    # teams=db.relationship("Team", backref="Company")
    teams=db.relationship("Team", backref="company")
    # HRManagers=db.relationship("HRManager", backref="Company")
    managers=db.relationship("HRManager", backref="company")
    
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
    '''clase para Team'''
    id= db.Column(db.Integer,primary_key= True)
    name=db.Column(db.String(120),unique=False)
    description=db.Column(db.String(200),unique=False)
    
    # Company_id = db.Column(db.Integer, db.ForeignKey("Company.id"))
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"))
    # members=db.relationship("HumanTalent", backref="Team")
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

    # HumanTalent_id=db.Column(db.Integer,db.ForeignKey("HumanTalent.id"))
    human_talent_id=db.Column(db.Integer,db.ForeignKey("humantalent.id"))

    def serialize(self):
        return{
            "id" : self.id,
            "date_published" : self.date_published,
            "face_value" : self.face_value,
            "comment" : self.comment,
                }
