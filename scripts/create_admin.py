import getpass
import os
import sys

from werkzeug.security import generate_password_hash

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app import create_app
from app.extensions import db
from app.models import User


def main():
    app = create_app()

    username = input("Admin username: ").strip()
    display_name = input("Display name: ").strip()
    email = input("Email address: ").strip()

    if not username:
        raise SystemExit("FAILED: Username is required")

    if not display_name:
        raise SystemExit("FAILED: Display name is required")

    password = getpass.getpass("Admin password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        raise SystemExit("FAILED: Passwords do not match")

    if len(password) < 12:
        raise SystemExit(
            "FAILED: Password must contain at least 12 characters"
        )

    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            raise SystemExit("FAILED: Username already exists")

        user = User(
            username=username,
            display_name=display_name,
            email=email or None,
            role="admin",
            is_active=True,
            password_hash=generate_password_hash(password),
        )

        db.session.add(user)
        db.session.commit()

        print(f"SUCCESS: Admin user created: {username}")


if __name__ == "__main__":
    main()
