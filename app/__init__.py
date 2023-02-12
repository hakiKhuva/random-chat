from flask import Flask
from flask_migrate import Migrate

import mimetypes
mimetypes.add_type("application/javascript", ".js")

from .config import APP_CONFIG

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.update(APP_CONFIG)
    
    app.static_folder = APP_CONFIG["STATIC_FOLDER"]

    from .socketio import socketio
    from .models.db import db

    socketio.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .views.message import message
    from .views.home import home

    for blueprint in [message, home]:
        app.register_blueprint(blueprint)

    return app