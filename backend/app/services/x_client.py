import requests
from typing import Dict, List, Optional
from datetime import datetime

from app.config import settings


class APIClientError(Exception):
    """Base exception for API client errors"""
    pass


def make_api_request(
    method: str,
    url: str,
    headers: Dict,
    params: Optional[Dict] = None,
    json: Optional[Dict] = None,
    error_context: str = "API request"
) -> Dict:
    """
    Make an API request with standardized error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Request headers
        params: Query parameters
        json: JSON body
        error_context: Context for error messages
        
    Returns:
        Response JSON
        
    Raises:
        APIClientError: If request fails
    """
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIClientError(f"{error_context}: {str(e)}")


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
        
        return make_api_request(
            method="POST",
            url=url,
            headers=self.headers,
            json=payload,
            error_context="Failed to post tweet"
        )
    
    def get_user_tweets(self, username: str, count: int = 10) -> List[Dict]:
        """Get recent tweets from a user"""
        url = f"{self.base_url}/twitter/user/tweets"
        params = {"userName": username, "count": count}
        
        result = make_api_request(
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            error_context="Failed to fetch tweets"
        )
        return result.get("tweets", [])
    
    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get metrics for a specific tweet"""
        url = f"{self.base_url}/twitter/tweet/metrics"
        params = {"tweetId": tweet_id}
        
        data = make_api_request(
            method="GET",
            url=url,
            headers=self.headers,
            params=params,
            error_context="Failed to fetch metrics"
        )
        
        return {
            "likes": data.get("like_count", 0),
            "retweets": data.get("retweet_count", 0),
            "replies": data.get("reply_count", 0),
            "impressions": data.get("impression_count"),
            "timestamp": datetime.utcnow()
        }


def get_twitter_client(api_key: str) -> TwitterAPIClient:
    """Factory function to create Twitter API client"""
    return TwitterAPIClient(api_key)