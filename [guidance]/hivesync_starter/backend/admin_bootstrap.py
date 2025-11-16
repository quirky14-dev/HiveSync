
import getpass

from app.db import Base, engine, SessionLocal
from app import models
from app.security import get_password_hash


def main():
    print("HiveSync Starter - Admin Bootstrap")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_admin = db.query(models.User).filter(models.User.is_admin == True).first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            return

        email = input("Enter admin email: ").strip()
        if not email:
            print("Email is required.")
            return

        password = getpass.getpass("Enter admin password: ")
        password_confirm = getpass.getpass("Confirm admin password: ")
        if password != password_confirm:
            print("Passwords do not match.")
            return

        hashed = get_password_hash(password)
        admin_user = models.User(
            email=email,
            hashed_password=hashed,
            is_active=True,
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Admin user created: {admin_user.email} (id={admin_user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
