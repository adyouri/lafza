from project.models import db, Term, Translation
from app import app
from flask import current_app

with app.app_context():
    db.create_all()
