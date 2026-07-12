from database import SessionLocal
from models.users import Role, User
from auth.security import hash_password

db = SessionLocal()

fm_role = db.query(Role).filter(Role.name == "Fleet Manager").first()
driver_role = db.query(Role).filter(Role.name == "Driver").first()

user1 = User(email="fm@test.com", hashed_password=hash_password("password123"), role_id=fm_role.id)
user2 = User(email="driver@test.com", hashed_password=hash_password("password123"), role_id=driver_role.id)

db.add_all([user1, user2])
db.commit()

print("Created users:")
print(user1.email, "-> hash:", user1.hashed_password)
print(user2.email, "-> hash:", user2.hashed_password)