from flask_sqlalchemy import SQLAlchemy
import os 
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode

db = SQLAlchemy()

class HumanTalent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(80), unique=False, nullable=False)
    full_name = db.Column(db.String(120), unique=False, nullable=False)
    user_type = db.Column(db.Integer)
    salt=db.Column(db.String(120),unique=False,nullable=False)
    team=relationship("Team", backref="HumanTalent")

    

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self):
        self.email=data["email"],
        self.salt=b64encode(os.urandom(4)).decode("utf-8")
        self.hashed_password=self.set.password(
            data["password"]
        )

    @classmethod
    def create(cls,data):
        User=cls(data)
        sb.session.add(user)
        db.session.commit()
        return User
    
    def set_password(self):
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
            "user_type":self.user_type,
            "hashed_password":self.hashed_password,
            "team_id":self.team_id
            }
        
class HRManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), unique=False, nullable=False)
    user_type = db.Column(db.Integer)
    salt=db.Column(db.String(120),unique=False,nullable=False)
    company=relationship("Company", backref="HRManager")
    hashed_password = db.Column(db.String(80), unique=False, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name":self.full_name,
            "user_type":self.user_type,
            "hashed_password":self.hashed_password,
            "company_id":self.company_id
            }

    class Team(db.Model):
        id= db.Column(db.Integer,primary_key=true
        name=db.Column(db.String(120),unique=False)
        company=relationship("Company", backref="Team")
        )

        def serialize(self):
            return{
                "id":self.id
                "name":self.name
                "company":self.company
            }