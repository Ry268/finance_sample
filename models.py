from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80), nullable=False)
    stock_code = db.Column(db.String(20), nullable=False)
