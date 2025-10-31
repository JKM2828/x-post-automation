def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        params={"username": "newuser", "twitter_username": "new_twitter"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["twitter_username"] == "new_twitter"
    assert "id" in data


def test_register_duplicate_user(client, test_user):
    """Test registering duplicate user fails"""
    response = client.post(
        "/auth/register",
        params={"username": "testuser", "twitter_username": "test"}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_user(client):
    """Test login with invalid user"""
    response = client.post(
        "/auth/login",
        json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401
