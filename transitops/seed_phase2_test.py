from datetime import date, timedelta
from database import SessionLocal
from models.fleet import Vehicle, Driver, MaintenanceLog

db = SessionLocal()

# Vehicles
van = Vehicle(
    registration_number="VAN-05",
    name_model="Tata Ace",
    type="Van",
    max_load_capacity=500,
    odometer=0,
    acquisition_cost=620000,
    status="Available"
)
db.add(van)
db.commit()
db.refresh(van)
print(f"Created vehicle: {van.registration_number}, id={van.id}, status={van.status}")

# Test uniqueness at DB level (expect this to fail/raise — that's correct)
try:
    dup = Vehicle(
        registration_number="VAN-05",
        name_model="Duplicate Test",
        type="Van",
        max_load_capacity=400,
        odometer=0,
        acquisition_cost=100000,
        status="Available"
    )
    db.add(dup)
    db.commit()
    print("ERROR: duplicate registration_number was allowed — uniqueness NOT enforced")
except Exception as e:
    db.rollback()
    print("OK: duplicate registration_number correctly rejected at DB level")

# Drivers
alex = Driver(
    name="Alex",
    license_number="DL-001",
    license_category="LMV",
    license_expiry_date=date.today() + timedelta(days=365),
    contact_number="9876500000",
    safety_score=95,
    status="Available"
)
john_expired = Driver(
    name="John",
    license_number="DL-002",
    license_category="LMV",
    license_expiry_date=date.today() - timedelta(days=10),
    contact_number="9822200000",
    safety_score=80,
    status="Available"
)
priya_suspended = Driver(
    name="Priya",
    license_number="DL-003",
    license_category="LMV",
    license_expiry_date=date.today() + timedelta(days=200),
    contact_number="9911100000",
    safety_score=70,
    status="Suspended"
)
db.add_all([alex, john_expired, priya_suspended])
db.commit()
print(f"Created drivers: Alex (valid), John (expired license), Priya (suspended)")

# Maintenance — create on VAN-05
maint = MaintenanceLog(
    vehicle_id=van.id,
    service_type="Oil Change",
    cost=2500,
    date=date.today(),
    status="Active"
)
db.add(maint)
db.commit()
db.refresh(van)
print(f"Created maintenance log. Vehicle status after creation: {van.status}")