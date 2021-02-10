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
    user_type = db.Column(db.Boolean)
    salt=db.Column(db.String(120),unique=False,nullable=False)
    

    # teams=relationship("Team", backref="HumanTalent")
    # post_likes = relationship('PostLike', backref = "user")
    # comments = relationship('Comment', backref = "author")
    # coment_likes = relationship('CommentLike', backref = "author")

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
        HumanTalent=cls(data)
        sb.session.add(HumanTalent)
        db.session.commit()
        return HumanTalent
    
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
            "user_type":False,
            "hashed_password":self.hashed_password
            }
        
class HRManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120), unique=False, nullable=False)
    user_type = db.Column(db.Boolean)
    salt=db.Column(db.String(120),unique=False,nullable=False)
    # company=relationship("Company", backref="HRManager")
    hashed_password = db.Column(db.String(80), unique=False, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name":self.full_name,
            "user_type":True,
            "hashed_password":self.hashed_password
            # "company_id":self.company_id
            }

    class Team(db.Model):
        id= db.Column(db.Integer,primary_key=true)
        name=db.Column(db.String(120),unique=False)
        # company=relationship("Company", backref="Team")
        

        def serialize(self):
            return{
                "id":self.id,
                "name":self.name,
                # "company":self.company
            }

    class Company(db.Model):
        id= db.Column(db.Integer,primary_key=true
        name=db.Column(db.String(120),unique=False)
        image=db.Column(sb.String(120),unique=False)
        country=db.Column(sb.String(120),unique=False)
        city=db.Column(db.String(120),unique=False)
        identifier=db.Column(db.String(120),unique=False)
        )
    
    def serialize(self):
            return{
                "id":self.id,
                "name":self.name,
                "image":self.image,
                "city":self.city,
                "country":self.country,
                "identifier":self.identifier
            }
    
    class Mood(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        date_published = db.Column(db.Integer)
        face_value = db.Column(db.Integer)
        comment = db.Column(db.String(120), unique=False, nullable=False)
        done=db.Column(db.Boolean)

     def serialize(self):
            return{
                "id"=self.id,
                "date_published"=self.date_published,
                "face_value"=self.face_value,
                "comment"=self.comment,
                "done"=False
            }