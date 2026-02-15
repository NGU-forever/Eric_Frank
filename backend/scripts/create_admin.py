#!/usr/bin/env python3
"""
Create Admin User Script

Usage:
    python scripts/create_admin.py --username admin --email admin@example.com --password admin123
"""
import sys
import os
import argparse

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db import SessionLocal, init_db
from app.api.v1.auth import get_password_hash
from app.models.database import User

def create_admin_user(username, email, password):
    init_db()
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_superuser=True
        )
        db.add(admin)
        db.commit()
        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create Admin User")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--email", default="admin@example.com", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    
    args = parser.parse_args()
    
    create_admin_user(args.username, args.email, args.password)
