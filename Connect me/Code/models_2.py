from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()
from flask_login import UserMixin

from app import db
from datetime import datetime

class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sponsor = db.relationship('Sponsor', backref='user', uselist=False)
    influencer = db.relationship('Influencer', backref='user', uselist=False)
    flags = db.relationship('Flag', backref='user')
    def get_id(self):
        return str(self.user_id)
    
    @property
    def is_active(self):
        return True

class Sponsor(db.Model):
    sponsor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.Numeric, nullable=False)

    campaigns = db.relationship('Campaign', backref='sponsor')

class Flag(db.Model):
    flag_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    reason = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Numeric, nullable=False)
    visibility = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)

    ad_requests = db.relationship('AdRequest', backref='campaign')

class Influencer(db.Model):
    influencer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=False)
    reach = db.Column(db.Integer, nullable=False)

    ad_requests = db.relationship('AdRequest', backref='influencer')

class AdRequest(db.Model):
    ad_request_id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'), nullable=False)
    messages = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Numeric, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending') 

























# class User(db.Model):
#  user_id = db.Column(db.Integer, primary_key=True)
#  username = db.Column(db.String(80), unique=True, nullable=False)
#  password = db.Column(db.String(120), nullable=False)
#  role = db.Column(db.String(10), nullable=False)
# created_at = db.Column(db.DateTime, default=datetime.utcnow)

# class Campaign(db.Model):
#  id = db.Column(db.Integer, primary_key=True)
#  name = db.Column(db.String(100), nullable=False)
#  description = db.Column(db.String(200), nullable=True)
#  start_date = db.Column(db.Date, nullable=False)
#  end_date = db.Column(db.Date, nullable=False)
#  budget = db.Column(db.Float, nullable=False)
#  visibility = db.Column(db.String(10), nullable=False)



# class AdRequest(db.Model):
#  id = db.Column(db.Integer, primary_key=True)
#  campaign_id = db.Column(db.Integer, 
#  db.ForeignKey('campaign.id'), nullable=False)
#  influencer_id = db.Column(db.Integer, 
#  db.ForeignKey('user.id'), nullable=False)
#  messages = db.Column(db.Text, nullable=True)
#  requirements = db.Column(db.Text, nullable=True)
#  payment_amount = db.Column(db.Float, nullable=False)
#  status = db.Column(db.String(10), nullable=False)























# 
# class User(db.Model):
#     d_id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(50), nullable=False)
#     films=db.relationship('Movie',backref="creator", secondary="association")
#     def __repr__(self) :
#         return f"<director {self.name}>"

# class Movie(db.Model):
#     m_id=db.Column(db.Integer ,primary_key=True)
#     name=db.Column(db.String(50), nullable=False)
  
   

#     def __repr__(self) :
#         return f"<movie {self.name}>"

# class Association(db.Model):
#       director_id=db.Column(db.Integer(), db.ForeignKey('director.d_id'),primary_key=True)
#       movie_id=db.Column(db.Integer(), db.ForeignKey('movie.m_id'),primary_key=True)
      