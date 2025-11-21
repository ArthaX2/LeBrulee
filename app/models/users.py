from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), unique=True, nullable=False)
    fullname = db.Column(db.String(32), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(200), nullable=True)

    def __init__(self, username, fullname, password, address=None):
        self.username = username
        self.fullname = fullname
        self.set_password(password)
        self.address = address

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)
