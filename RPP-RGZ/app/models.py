from . import db

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    periodicity = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)