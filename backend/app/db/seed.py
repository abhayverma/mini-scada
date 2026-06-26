from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash

def seed_db(db: Session):
    # Check if admin exists; if not, create default users
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role="admin"
        )
        dispatcher = User(
            username="dispatcher",
            password_hash=get_password_hash("dispatch123"),
            role="dispatcher"
        )
        operator = User(
            username="operator",
            password_hash=get_password_hash("operator123"),
            role="operator"
        )
        db.add_all([admin, dispatcher, operator])
        db.commit()