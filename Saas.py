import os
from flask import request, g
from .models import Tenant
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, request, jsonify, g
from .models import db, User
from flask import Flask
from app.models import db
from app.routes import bp
from app.tenant_middleware import tenant_middleware
from config import Config

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/saas_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

db = SQLAlchemy()

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    domain = db.Column(db.String(100), unique=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'))
    username = db.Column(db.String(50))
    email = db.Column(db.String(100))

def tenant_middleware(app):
    @app.before_request
    def identify_tenant():
        host = request.host.split(':')[0]
        tenant = Tenant.query.filter_by(domain=host).first()
        if not tenant:
            return "Tenant not found", 404
        g.tenant = tenant

bp = Blueprint('routes', __name__)

@bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.filter_by(tenant_id=g.tenant.id).all()
    return jsonify([{"username": u.username, "email": u.email} for u in users])

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
tenant_middleware(app)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)




