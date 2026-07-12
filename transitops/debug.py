from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.get("/")
print("STATUS:", response.status_code)
print("BODY:", response.text)