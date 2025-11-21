import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # common for all
    # Gmail SMTP Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "arthasuryapratama46@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # Will be set via environment variable (App Password)
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME", "arthasuryapratama46@gmail.com")
    # Recipient email for contact form submissions
    CONTACT_EMAIL = "arthasuryapratama46@gmail.com"


class DevConf(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI", "sqlite:///dev.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")


class ProdConf(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI", "sqlite:///prod.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-secret-key")
