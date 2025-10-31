from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta

from app.database import get_db
from app import models, schemas
from app.auth.dependencies import create_access_token
from app.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

@router.post("/register", response_model=schemas.User)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    
    # Check if user exists
    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = models.User(
        username=user_data.username,
        twitter_username=user_data.twitter_username,
        api_key=user_data.api_key  # Should be encrypted in production
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "twitter_username": user.twitter_username
        }
    }

@router.post("/x/callback")
async def x_oauth_callback(code: str, db: Session = Depends(get_db)):
    """Handle X OAuth callback"""
    # TODO: Implement X OAuth flow
    return {"status": "success", "message": "OAuth callback received"}