from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
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
    """Get analytics summary for the user"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get total tweets
    total_tweets = db.query(func.count(models.Tweet.id)).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.status == "posted",
        models.Tweet.posted_at >= cutoff_date
    ).scalar()
    
    # Get total engagement
    engagement_stats = db.query(
        func.sum(models.Metric.likes).label("total_likes"),
        func.sum(models.Metric.retweets).label("total_retweets"),
        func.sum(models.Metric.replies).label("total_replies"),
        func.avg(models.Metric.engagement_rate).label("avg_engagement")
    ).join(
        models.Tweet
    ).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= cutoff_date
    ).first()
    
    total_engagement = (
        (engagement_stats.total_likes or 0) +
        (engagement_stats.total_retweets or 0) +
        (engagement_stats.total_replies or 0)
    )
    
    # Get top tweet
    top_tweet = db.query(models.Tweet).join(
        models.Metric
    ).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= cutoff_date
    ).order_by(
        (models.Metric.likes + models.Metric.retweets + models.Metric.replies).desc()
    ).first()
    
    # Get best time slots (by hour)
    best_times = db.query(
        func.extract('hour', models.Tweet.posted_at).label("hour"),
        func.avg(models.Metric.engagement_rate).label("avg_engagement")
    ).join(
        models.Metric
    ).filter(
        models.Tweet.user_id == current_user.id,
        models.Tweet.posted_at >= cutoff_date
    ).group_by(
        func.extract('hour', models.Tweet.posted_at)
    ).order_by(
        func.avg(models.Metric.engagement_rate).desc()
    ).limit(5).all()
    
    best_time_slots = [
        {"hour": int(time.hour), "avg_engagement": float(time.avg_engagement or 0)}
        for time in best_times
    ]
    
    return {
        "total_tweets": total_tweets or 0,
        "total_engagement": total_engagement,
        "avg_engagement_rate": float(engagement_stats.avg_engagement or 0),
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
    
    # Verify tweet ownership
    tweet = db.query(models.Tweet).filter(
        models.Tweet.id == tweet_id,
        models.Tweet.user_id == current_user.id
    ).first()
    
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    metrics = db.query(models.Metric).filter(
        models.Metric.tweet_id == tweet_id
    ).order_by(models.Metric.timestamp.desc()).all()
    
    return metrics


@router.get("/engagement-trends")
async def get_engagement_trends(
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get engagement trends over time"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    trends = db.query(
        func.date(models.Metric.timestamp).label("date"),
        func.sum(models.Metric.likes).label("total_likes"),
        func.sum(models.Metric.retweets).label("total_retweets"),
        func.sum(models.Metric.replies).label("total_replies"),
        func.avg(models.Metric.engagement_rate).label("avg_engagement")
    ).join(
        models.Tweet
    ).filter(
        models.Tweet.user_id == current_user.id,
        models.Metric.timestamp >= cutoff_date
    ).group_by(
        func.date(models.Metric.timestamp)
    ).order_by(
        func.date(models.Metric.timestamp)
    ).all()
    
    return [
        {
            "date": str(trend.date),
            "likes": trend.total_likes or 0,
            "retweets": trend.total_retweets or 0,
            "replies": trend.total_replies or 0,
            "avg_engagement": float(trend.avg_engagement or 0)
        }
        for trend in trends
    ]
