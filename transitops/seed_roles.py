from database import SessionLocal, Base, engine
from models.users import Role, User
from auth.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

roles = ["Fleet Manager", "Driver", "Safety Officer", "Financial Analyst"]
for r in roles:
    db.add(Role(name=r))
db.commit()

print(db.query(Role).all())