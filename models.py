from app import db
from sqlalchemy.dialects.postgresql import JSON

class Department(db.model):
  __tablename__ = 'department'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String())

  