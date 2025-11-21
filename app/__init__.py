from flask import Flask
import os
from dotenv import load_dotenv

from app.extensions import db, migrate, login_manager, mail
from app.configs import DevConf, ProdConf

from app.routes.main_bp import main_bp
from app.routes.auth_bp import auth_bp

load_dotenv()

isDev = os.getenv("FLASK_DEBUG")


def create_app():
    app = Flask(__name__)

    # Load environment-specific config
    if isDev:
        app.config.from_object(DevConf)
    else:
        app.config.from_object(ProdConf)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)   # <-- initialize first

    # Configure login_manager AFTER init_app
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.session_protection = "strong"

    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
