from database import SessionLocal
from models.users import User, Role

db = SessionLocal()
users = db.query(User).all()

if not users:
    print("NO USERS FOUND")
else:
    for u in users:
        print(f"email={u.email}, role={u.role.name}, hash_prefix={u.hashed_password[:7]}")