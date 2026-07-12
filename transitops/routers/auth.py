from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from schemas.users import UserLogin
from models.users import User
from auth.dependencies import get_db
from auth.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login")
def login(user_credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/logout")
def logout(response: Response):
    return {"message": "Successfully logged out. Please clear the token on the client side."}
