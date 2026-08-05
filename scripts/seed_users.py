"""Create initial HR and employee accounts for testing.

Run with: python -m scripts.seed_users
"""
from app.auth import hash_password
from app.database import SessionLocal
from app.models import Role, User

SEED_USERS = [
    ("hr@example.com", "hrpassword123", Role.hr),
    ("employee@example.com", "employeepassword123", Role.employee),
]


def main():
    db = SessionLocal()
    try:
        for email, password, role in SEED_USERS:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                print(f"Skipping {email}, already exists.")
                continue
            user = User(email=email, password_hash=hash_password(password), role=role)
            db.add(user)
            print(f"Created {role.value} user: {email} / {password}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
