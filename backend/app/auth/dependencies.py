"""Authentication dependencies for FastAPI"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user from token.
    
    Args:
        token: OAuth2 token
        db: Database session
        
    Returns:
        User model instance
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    # This is a stub implementation
    # In production, this would validate the JWT token and return the user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # For now, return a stub
    raise credentials_exception
