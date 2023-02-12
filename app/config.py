import os

APP_NAME = "Random Chat"

APP_CONFIG = {
    "SECRET_KEY": os.environ.get("SECRET_KEY", os.urandom(20)),
    "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URI", "sqlite:///master.sqlite"),
    "STATIC_FOLDER": "static"
}
