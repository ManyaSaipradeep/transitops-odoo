from pydantic import BaseModel, ConfigDict

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
