from flask import Flask
import os
from dotenv import load_dotenv

from app.extensions import db, migrate, login_manager
from app.configs import DevConf, ProdConf

from app.routes.main_bp import main_bp
from app.routes.auth_bp import auth_bp

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Determine environment
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        app.config.from_object(ProdConf)
    else:
        app.config.from_object(DevConf)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Where to redirect when login is required
    login_manager.login_view = "auth.login"

    # ------------------------------
    # 🔥 FIXED BLUEPRINT REGISTRATION
    # ------------------------------
    app.register_blueprint(main_bp, url_prefix="")           # Main pages (/, /menu, /cart, etc.)
    app.register_blueprint(auth_bp, url_prefix="/auth")      # Login, signup, logout

    return app
