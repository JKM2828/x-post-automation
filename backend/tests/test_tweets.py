def test_create_tweet(client, auth_headers):
    """Test creating a tweet"""
    response = client.post(
        "/api/tweets/",
        json={"text": "Test tweet content", "media_links": []},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Test tweet content"
    assert data["status"] == "draft"
    assert data["generated_by_ai"] is False


def test_create_scheduled_tweet(client, auth_headers):
    """Test creating a scheduled tweet"""
    from datetime import datetime, timedelta
    scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    response = client.post(
        "/api/tweets/",
        json={
            "text": "Scheduled tweet",
            "media_links": [],
            "scheduled_at": scheduled_time
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "scheduled"


def test_get_tweets(client, auth_headers):
    """Test getting all tweets"""
    # Create a tweet first
    client.post(
        "/api/tweets/",
        json={"text": "Test tweet", "media_links": []},
        headers=auth_headers
    )
    
    response = client.get("/api/tweets/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_tweet_by_id(client, auth_headers):
    """Test getting specific tweet"""
    # Create a tweet
    create_response = client.post(
        "/api/tweets/",
        json={"text": "Test tweet", "media_links": []},
        headers=auth_headers
    )
    tweet_id = create_response.json()["id"]
    
    response = client.get(f"/api/tweets/{tweet_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tweet_id
    assert data["text"] == "Test tweet"


def test_get_nonexistent_tweet(client, auth_headers):
    """Test getting nonexistent tweet"""
    response = client.get("/api/tweets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_unauthorized_access(client):
    """Test accessing tweets without auth"""
    response = client.get("/api/tweets/")
    assert response.status_code == 403
