"""Common utility functions for the application"""
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def get_user_tweet_or_404(
    db: Session,
    tweet_id: int,
    user_id: int
) -> models.Tweet:
    """
    Fetch a tweet belonging to a specific user or raise 404.
    
    Args:
        db: Database session
        tweet_id: ID of the tweet to fetch
        user_id: ID of the user who should own the tweet
        
    Returns:
        Tweet model instance
        
    Raises:
        HTTPException: 404 if tweet not found or doesn't belong to user
    """
    tweet = db.query(models.Tweet).filter(
        models.Tweet.id == tweet_id,
        models.Tweet.user_id == user_id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    return tweet


def handle_api_error(error: Exception, context: str, status_code: int = 500) -> HTTPException:
    """
    Create a standardized HTTPException from an API error.
    
    Args:
        error: The original exception
        context: Context message (e.g., "AI generation failed", "Failed to post")
        status_code: HTTP status code to return
        
    Returns:
        HTTPException with formatted error message
    """
    return HTTPException(
        status_code=status_code,
        detail=f"{context}: {str(error)}"
    )
