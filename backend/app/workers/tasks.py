from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app import models
from app.services.x_client import get_twitter_client
from app.config import settings

logger = logging.getLogger(__name__)


def get_db():
    """Get database session for tasks"""
    db = SessionLocal()
    return db


@celery_app.task(name='app.workers.tasks.post_scheduled_tweets')
def post_scheduled_tweets():
    """
    Post tweets that are scheduled for now or earlier
    """
    db = get_db()
    
    try:
        now = datetime.utcnow()
        
        # Get scheduled tweets
        scheduled_tweets = db.query(models.Tweet).filter(
            models.Tweet.status == "scheduled",
            models.Tweet.scheduled_at <= now
        ).all()
        
        logger.info(f"Found {len(scheduled_tweets)} tweets to post")
        
        for tweet in scheduled_tweets:
            try:
                # Get user
                user = db.query(models.User).filter(
                    models.User.id == tweet.user_id
                ).first()
                
                if not user or not user.api_key:
                    logger.warning(f"No API key for user {tweet.user_id}")
                    continue
                
                # Post to Twitter
                twitter_client = get_twitter_client(user.api_key)
                result = twitter_client.post_tweet(tweet.text, tweet.media_links)
                
                # Update tweet
                tweet.tweet_id_twitter = result.get("id_str")
                tweet.status = "posted"
                tweet.posted_at = datetime.utcnow()
                
                logger.info(f"Posted tweet {tweet.id} successfully")
                
            except Exception as e:
                logger.error(f"Failed to post tweet {tweet.id}: {str(e)}")
                tweet.status = "failed"
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error in post_scheduled_tweets: {str(e)}")
        db.rollback()
    finally:
        db.close()


@celery_app.task(name='app.workers.tasks.fetch_tweet_metrics')
def fetch_tweet_metrics():
    """
    Fetch metrics for recently posted tweets
    """
    db = get_db()
    
    try:
        # Get posted tweets from last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        tweets = db.query(models.Tweet).filter(
            models.Tweet.status == "posted",
            models.Tweet.posted_at >= cutoff_date,
            models.Tweet.tweet_id_twitter.isnot(None)
        ).all()
        
        logger.info(f"Fetching metrics for {len(tweets)} tweets")
        
        for tweet in tweets:
            try:
                # Get user
                user = db.query(models.User).filter(
                    models.User.id == tweet.user_id
                ).first()
                
                if not user or not user.api_key:
                    continue
                
                # Fetch metrics
                twitter_client = get_twitter_client(user.api_key)
                metrics_data = twitter_client.get_tweet_metrics(tweet.tweet_id_twitter)
                
                # Save metrics
                metric = models.Metric(
                    tweet_id=tweet.id,
                    likes=metrics_data.get("likes", 0),
                    retweets=metrics_data.get("retweets", 0),
                    replies=metrics_data.get("replies", 0),
                    impressions=metrics_data.get("impressions"),
                    timestamp=datetime.utcnow()
                )
                
                # Calculate engagement rate
                if metrics_data.get("impressions"):
                    total_engagement = (
                        metrics_data.get("likes", 0) + 
                        metrics_data.get("retweets", 0) + 
                        metrics_data.get("replies", 0)
                    )
                    metric.engagement_rate = total_engagement / metrics_data["impressions"]
                
                db.add(metric)
                logger.info(f"Saved metrics for tweet {tweet.id}")
                
            except Exception as e:
                logger.error(f"Failed to fetch metrics for tweet {tweet.id}: {str(e)}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error in fetch_tweet_metrics: {str(e)}")
        db.rollback()
    finally:
        db.close()


@celery_app.task(name='app.workers.tasks.retrain_viral_model')
def retrain_viral_model():
    """
    Retrain the viral prediction ML model with new data
    """
    db = get_db()
    
    try:
        logger.info("Starting viral model retraining...")
        
        # Get tweets with metrics for training
        tweets_with_metrics = db.query(models.Tweet).join(
            models.Metric
        ).filter(
            models.Tweet.status == "posted"
        ).all()
        
        logger.info(f"Found {len(tweets_with_metrics)} tweets for training")
        
        # TODO: Implement ML model training
        # This would involve:
        # 1. Extract features from tweets (text, timing, hashtags, etc.)
        # 2. Calculate viral score from metrics
        # 3. Train XGBoost/LightGBM model
        # 4. Save model to MODEL_PATH
        
        logger.info("Model retraining completed (placeholder)")
        
    except Exception as e:
        logger.error(f"Error in retrain_viral_model: {str(e)}")
    finally:
        db.close()
