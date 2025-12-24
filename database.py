from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Violation(db.Model):
    __tablename__ = "violations"

    id = db.Column(db.Integer, primary_key=True)
    violation_type = db.Column(db.String(50), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
