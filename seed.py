from models import User
from app import db

db.drop_all()
db.create_all()
