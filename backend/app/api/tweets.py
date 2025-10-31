from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.auth.dependencies import get_current_user
from app.services.x_client import get_twitter_client

router = APIRouter()


@router.post("/", response_model=schemas.Tweet, status_code=status.HTTP_201_CREATED)
async def create_tweet(
    tweet_data: schemas.TweetCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new tweet (draft or scheduled)"""
    
    tweet = models.Tweet(
        user_id=current_user.id,
        text=tweet_data.text,
        media_links=tweet_data.media_links,
        scheduled_at=tweet_data.scheduled_at,
        status="scheduled" if tweet_data.scheduled_at else "draft"
    )
    
    db.add(tweet)
    db.commit()
    db.refresh(tweet)
    
    return tweet


@router.get("/", response_model=List[schemas.Tweet])
async def get_tweets(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tweets for current user"""
    
    query = db.query(models.Tweet).filter(models.Tweet.user_id == current_user.id)
    
    if status:
        query = query.filter(models.Tweet.status == status)
    
    tweets = query.order_by(models.Tweet.created_at.desc()).limit(limit).all()
    return tweets


@router.get("/{tweet_id}", response_model=schemas.Tweet)
async def get_tweet(
    tweet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific tweet"""
    
    tweet = db.query(models.Tweet).filter(
        models.Tweet.id == tweet_id,
        models.Tweet.user_id == current_user.id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    return tweet


@router.post("/{tweet_id}/post", response_model=schemas.Tweet)
async def post_tweet_now(
    tweet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Post tweet immediately to Twitter"""
    
    tweet = db.query(models.Tweet).filter(
        models.Tweet.id == tweet_id,
        models.Tweet.user_id == current_user.id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    if tweet.status == "posted":
        raise HTTPException(status_code=400, detail="Tweet already posted")
    
    if not current_user.api_key:
        raise HTTPException(status_code=400, detail="Twitter API key not configured")
    
    # Post to Twitter
    try:
        twitter_client = get_twitter_client(current_user.api_key)
        result = twitter_client.post_tweet(tweet.text, tweet.media_links)
        
        tweet.tweet_id_twitter = result.get("id_str")
        tweet.status = "posted"
        tweet.posted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tweet)
        
        return tweet
        
    except Exception as e:
        tweet.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to post: {str(e)}")
