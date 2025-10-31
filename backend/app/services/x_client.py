import requests
from typing import Dict, List, Optional
from datetime import datetime

from app.config import settings


class TwitterAPIClient:
    """
    Client for unofficial Twitter API (twitterapi.io)
    Much cheaper alternative to official X API v2
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.twitterapi.io"
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def post_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> Dict:
        """Post a new tweet"""
        url = f"{self.base_url}/twitter/tweet"
        payload = {"text": text[:280]}
        if media_ids:
            payload["media_ids"] = media_ids
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to post tweet: {str(e)}")
    
    def get_user_tweets(self, username: str, count: int = 10) -> List[Dict]:
        """Get recent tweets from a user"""
        url = f"{self.base_url}/twitter/user/tweets"
        params = {"userName": username, "count": count}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json().get("tweets", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch tweets: {str(e)}")
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get metrics for a specific tweet"""
        url = f"{self.base_url}/twitter/tweet/metrics"
        params = {"tweetId": tweet_id}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                "likes": data.get("like_count", 0),
                "retweets": data.get("retweet_count", 0),
                "replies": data.get("reply_count", 0),
                "impressions": data.get("impression_count"),
                "timestamp": datetime.utcnow()
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch metrics: {str(e)}")


def get_twitter_client(api_key: str) -> TwitterAPIClient:
    """Factory function to create Twitter API client"""
    return TwitterAPIClient(api_key)