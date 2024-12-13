from flask import Flask, request, jsonify
from models import db, User, Subscription

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/yourdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
