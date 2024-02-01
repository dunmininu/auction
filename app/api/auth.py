from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..utils.auth import (
    authenticate_user, 
    create_access_token, 
    create_user, 
    get_db, 
    get_user_by_email, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..models.user import UserCreate

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user_db = authenticate_user(db, form_data.username, form_data.password)
    if not user_db:
        raise HTTPException(
            status_code=HTTPException.status_code,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_db.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    return create_user(db=db, user=user)