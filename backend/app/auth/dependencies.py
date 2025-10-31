from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models

# Security scheme for bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get current authenticated user from JWT token.
    
    For now, this is a simplified version that should be replaced with
    proper JWT token validation in production.
    """
    token = credentials.credentials
    
    # TODO: Implement proper JWT token validation
    # For now, we'll do a simple lookup by treating token as username
    # This is NOT secure and should be replaced with proper JWT validation
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Simple lookup - REPLACE WITH PROPER JWT VALIDATION
    user = db.query(models.User).filter(models.User.username == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Dependency to get current active user.
    Can be extended to check if user is active/verified.
    """
    # Add checks here if needed (e.g., user.is_active)
    return current_user
