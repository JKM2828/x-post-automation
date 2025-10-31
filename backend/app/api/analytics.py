from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/summary", response_model=schemas.AnalyticsSummary)
async def get_analytics_summary(
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics summary for user"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Get total tweets
    total_tweets = db.query(models.Tweet).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.status == "posted",
        models.Tweet.posted_at >= since_date
    ).count()
    
    # Get total engagement
    engagement_query = db.query(
        func.sum(models.Metric.likes + models.Metric.retweets + models.Metric.replies).label('total')
    ).join(models.Tweet).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= since_date
    ).first()
    
    total_engagement = engagement_query.total or 0
    
    # Get average engagement rate
    avg_engagement = db.query(
        func.avg(models.Metric.engagement_rate).label('avg')
    ).join(models.Tweet).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= since_date
    ).first()
    
    avg_engagement_rate = float(avg_engagement.avg or 0)
    
    # Get top tweet
    top_tweet = db.query(models.Tweet).join(models.Metric).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= since_date
    ).order_by(desc(models.Metric.likes + models.Metric.retweets)).first()
    
    # Get best time slots (hour of day)
    best_times = db.query(
        func.extract('hour', models.Tweet.posted_at).label('hour'),
        func.avg(models.Metric.engagement_rate).label('avg_engagement')
    ).join(models.Metric).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= since_date
    ).group_by('hour').order_by(desc('avg_engagement')).limit(5).all()
    
    best_time_slots = [
        {"hour": int(hour), "avg_engagement": float(eng)} 
        for hour, eng in best_times
    ]
    
    return {
        "total_tweets": total_tweets,
        "total_engagement": int(total_engagement),
        "avg_engagement_rate": avg_engagement_rate,
        "top_tweet": top_tweet,
        "best_time_slots": best_time_slots
    }


@router.get("/tweets/{tweet_id}/metrics", response_model=List[schemas.Metric])
async def get_tweet_metrics(
    tweet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metrics history for a specific tweet"""
    
    tweet = db.query(models.Tweet).filter(
        models.Tweet.id == tweet_id,
        models.Tweet.user_id == current_user.id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    metrics = db.query(models.Metric).filter(
        models.Metric.tweet_id == tweet_id
    ).order_by(models.Metric.timestamp).all()
    
    return metrics


@router.get("/engagement-over-time")
async def get_engagement_over_time(
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get engagement metrics over time"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    daily_stats = db.query(
        func.date(models.Tweet.posted_at).label('date'),
        func.count(models.Tweet.id).label('tweets'),
        func.sum(models.Metric.likes).label('likes'),
        func.sum(models.Metric.retweets).label('retweets'),
        func.sum(models.Metric.replies).label('replies')
    ).join(models.Metric).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= since_date
    ).group_by('date').order_by('date').all()
    
    return {
        "data": [
            {
                "date": str(stat.date),
                "tweets": stat.tweets,
                "likes": stat.likes or 0,
                "retweets": stat.retweets or 0,
                "replies": stat.replies or 0,
                "total_engagement": (stat.likes or 0) + (stat.retweets or 0) + (stat.replies or 0)
            }
            for stat in daily_stats
        ]
    }


@router.get("/top-tweets")
async def get_top_tweets(
    limit: int = 10,
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top performing tweets"""
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    top_tweets = db.query(
        models.Tweet,
        (models.Metric.likes + models.Metric.retweets + models.Metric.replies).label('engagement')
    ).join(models.Metric).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= since_date
    ).order_by(desc('engagement')).limit(limit).all()
    
    return {
        "tweets": [
            {
                "id": tweet.id,
                "text": tweet.text,
                "posted_at": tweet.posted_at,
                "engagement": engagement,
                "viral_score": tweet.viral_score
            }
            for tweet, engagement in top_tweets
        ]
    }