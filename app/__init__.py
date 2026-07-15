import os

from flask import Flask

from .extensions import db, login_manager
from .models import User


def create_app():
    app = Flask(__name__)

    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_port = os.environ["DB_PORT"]
    db_name = os.environ["DB_NAME"]

    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://"
        f"{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "..",
        "uploads",
    )

    app.config["UPLOAD_FOLDER"] = os.path.abspath(
        app.config["UPLOAD_FOLDER"]
    )

    app.config["UPLOAD_DIR"] = os.environ["UPLOAD_DIR"]
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth_bp
    from .main import main_bp
    from .operation_plans import operation_plans_bp
    from .accounts import accounts_bp
    from .check_items import check_items_bp
    from .change_requests import change_requests_bp
    from .incidents import incidents_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(operation_plans_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(check_items_bp)
    app.register_blueprint(change_requests_bp)
    app.register_blueprint(incidents_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
